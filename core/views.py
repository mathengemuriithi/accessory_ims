from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_POST
import datetime
from decimal import Decimal

from .models import Product, Category, Sale, StockReconciliation, StoreSettings, UserProfile
from .forms import ProductForm, CategoryForm, ReconciliationForm, AttendantForm, StoreSetupForm
from .utils import generate_sales_pdf
from .decorators import admin_required


# ─── Auth & Setup ────────────────────────────────────────────────────────────

def setup_view(request):
    store = StoreSettings.get_settings()
    if store.is_setup_complete:
        return redirect('login')

    if request.method == 'POST':
        form = StoreSetupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Save store name
            store.store_name = data['store_name']
            store.is_setup_complete = True
            store.save()
            # Create categories
            for cat_name in data['categories'].split(','):
                cat_name = cat_name.strip()
                if cat_name:
                    Category.objects.get_or_create(name=cat_name)
            # Create admin user
            user = User.objects.create_user(
                username=data['admin_username'],
                password=data['admin_password']
            )
            user.profile.role = 'admin'
            user.profile.save()
            messages.success(request, f'Store "{store.store_name}" is ready. Please log in.')
            return redirect('login')
    else:
        form = StoreSetupForm()

    return render(request, 'core/setup.html', {'form': form})


def login_view(request):
    store = StoreSettings.get_settings()
    if not store.is_setup_complete:
        return redirect('setup')

    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html', {'store': store})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_admin:
        return redirect('admin_dashboard')
    return redirect('attendant_dashboard')


# ─── Admin Views ──────────────────────────────────────────────────────────────

@login_required
@admin_required
def admin_dashboard(request):
    store = StoreSettings.get_settings()
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    today_end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))

    today_sales = Sale.objects.filter(timestamp__range=(today_start, today_end))
    today_revenue = today_sales.aggregate(total=Sum('selling_price') * Sum('quantity'))
    # Calculate properly
    today_revenue = sum(s.total for s in today_sales)
    today_profit = sum(s.profit for s in today_sales)
    today_count = today_sales.count()

    low_stock = Product.objects.filter(quantity__lte=5).order_by('quantity')
    recent_sales = today_sales.select_related('attendant')[:10]

    # Last 7 days chart data
    chart_labels = []
    chart_revenue = []
    chart_profit = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = timezone.make_aware(datetime.datetime.combine(day, datetime.time.min))
        day_end = timezone.make_aware(datetime.datetime.combine(day, datetime.time.max))
        day_sales = Sale.objects.filter(timestamp__range=(day_start, day_end))
        rev = sum(s.total for s in day_sales)
        prof = sum(s.profit for s in day_sales)
        chart_labels.append(day.strftime('%d %b'))
        chart_revenue.append(float(rev))
        chart_profit.append(float(prof))

    context = {
        'store': store,
        'today': today,
        'today_revenue': today_revenue,
        'today_profit': today_profit,
        'today_count': today_count,
        'low_stock': low_stock,
        'recent_sales': recent_sales,
        'chart_labels': chart_labels,
        'chart_revenue': chart_revenue,
        'chart_profit': chart_profit,
        'total_products': Product.objects.count(),
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
@admin_required
def products_list(request):
    store = StoreSettings.get_settings()
    search = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.select_related('category').all()
    if search:
        products = products.filter(name__icontains=search)
    if category_filter:
        products = products.filter(category__id=category_filter)

    categories = Category.objects.all()
    context = {
        'store': store,
        'products': products,
        'categories': categories,
        'search': search,
        'category_filter': category_filter,
    }
    return render(request, 'core/products.html', context)


@login_required
@admin_required
def product_add(request):
    store = StoreSettings.get_settings()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('products_list')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'store': store, 'action': 'Add'})


@login_required
@admin_required
def product_edit(request, pk):
    store = StoreSettings.get_settings()
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'store': store, 'action': 'Edit', 'product': product})


@login_required
@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'"{product.name}" deleted.')
        return redirect('products_list')
    store = StoreSettings.get_settings()
    return render(request, 'core/product_confirm_delete.html', {'product': product, 'store': store})


@login_required
@admin_required
def sales_history(request):
    store = StoreSettings.get_settings()
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            filter_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            filter_date = timezone.localdate()
    else:
        filter_date = timezone.localdate()

    day_start = timezone.make_aware(datetime.datetime.combine(filter_date, datetime.time.min))
    day_end = timezone.make_aware(datetime.datetime.combine(filter_date, datetime.time.max))
    sales = Sale.objects.filter(timestamp__range=(day_start, day_end)).select_related('attendant', 'product')

    total_revenue = sum(s.total for s in sales)
    total_profit = sum(s.profit for s in sales)

    context = {
        'store': store,
        'sales': sales,
        'filter_date': filter_date,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
    }
    return render(request, 'core/sales_history.html', context)


@login_required
@admin_required
def sales_pdf(request):
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            filter_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            filter_date = timezone.localdate()
    else:
        filter_date = timezone.localdate()

    day_start = timezone.make_aware(datetime.datetime.combine(filter_date, datetime.time.min))
    day_end = timezone.make_aware(datetime.datetime.combine(filter_date, datetime.time.max))
    sales = Sale.objects.filter(timestamp__range=(day_start, day_end)).select_related('attendant')

    store = StoreSettings.get_settings()
    pdf_buffer = generate_sales_pdf(sales, store.store_name, filter_date)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales-{filter_date}.pdf"'
    return response


@login_required
@admin_required
def reconciliation_list(request):
    store = StoreSettings.get_settings()
    records = StockReconciliation.objects.select_related('product', 'recorded_by').all()[:50]
    context = {'store': store, 'records': records}
    return render(request, 'core/reconciliation_list.html', context)


@login_required
@admin_required
def categories_list(request):
    store = StoreSettings.get_settings()
    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')
    form = CategoryForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category added.')
                return redirect('categories_list')
        elif action == 'delete':
            cat_id = request.POST.get('cat_id')
            cat = get_object_or_404(Category, pk=cat_id)
            cat.delete()
            messages.success(request, f'"{cat.name}" deleted.')
            return redirect('categories_list')

    context = {'store': store, 'categories': categories, 'form': form}
    return render(request, 'core/categories.html', context)


@login_required
@admin_required
def users_list(request):
    store = StoreSettings.get_settings()
    attendants = User.objects.filter(profile__role='attendant').select_related('profile')
    form = AttendantForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = AttendantForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user = User.objects.create_user(
                    username=data['username'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                )
                user.profile.role = 'attendant'
                user.profile.save()
                messages.success(request, f'Attendant "{user.username}" added.')
                return redirect('users_list')
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            user.delete()
            messages.success(request, 'Attendant removed.')
            return redirect('users_list')

    context = {'store': store, 'attendants': attendants, 'form': form}
    return render(request, 'core/users.html', context)


# ─── Attendant Views ─────────────────────────────────────────────────────────

@login_required
def attendant_dashboard(request):
    store = StoreSettings.get_settings()
    search = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.select_related('category').filter(quantity__gt=0)
    if search:
        products = products.filter(name__icontains=search)
    if category_filter:
        products = products.filter(category__id=category_filter)

    categories = Category.objects.all()

    # Today's sales by this attendant
    today = timezone.localdate()
    today_start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    today_end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
    my_sales_today = Sale.objects.filter(
        attendant=request.user,
        timestamp__range=(today_start, today_end)
    ).count()

    context = {
        'store': store,
        'products': products,
        'categories': categories,
        'search': search,
        'category_filter': category_filter,
        'my_sales_today': my_sales_today,
    }
    return render(request, 'core/attendant_dashboard.html', context)


@login_required
@require_POST
def sell_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'Invalid quantity.')
        return redirect('attendant_dashboard')

    if product.quantity < quantity:
        messages.error(request, f'Not enough stock. Only {product.quantity} available.')
        return redirect('attendant_dashboard')

    Sale.objects.create(
        product=product,
        product_name=product.name,
        selling_price=product.selling_price,
        buying_price=product.buying_price,
        quantity=quantity,
        attendant=request.user,
    )
    product.quantity -= quantity
    product.save()

    messages.success(request, f'Sold {quantity}x {product.name} — KES {product.selling_price * quantity:,.2f}')
    return redirect('attendant_dashboard')


@login_required
def reconciliation_form(request):
    store = StoreSettings.get_settings()
    form = ReconciliationForm()

    if request.method == 'POST':
        form = ReconciliationForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            physical_count = form.cleaned_data['physical_count']
            notes = form.cleaned_data.get('notes', '')
            system_count = product.quantity
            discrepancy = physical_count - system_count

            if discrepancy == 0:
                rec_type = 'matched'
            elif discrepancy < 0:
                rec_type = 'shrinkage'
            else:
                rec_type = 'surplus'

            StockReconciliation.objects.create(
                product=product,
                product_name=product.name,
                system_count=system_count,
                physical_count=physical_count,
                discrepancy=discrepancy,
                reconciliation_type=rec_type,
                notes=notes,
                recorded_by=request.user,
            )

            # Adjust stock to match physical count
            product.quantity = physical_count
            product.save()

            messages.success(request, f'Reconciliation logged for "{product.name}". Stock updated to {physical_count}.')
            if hasattr(request.user, 'profile') and request.user.profile.is_admin:
                return redirect('reconciliation_list')
            return redirect('attendant_dashboard')

    context = {'store': store, 'form': form}
    return render(request, 'core/reconciliation_form.html', context)

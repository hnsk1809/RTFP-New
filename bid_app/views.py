from datetime import datetime, timezone
from email import message
from math import prod
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import random
import math
from django.conf import settings
from django.core.mail import EmailMessage

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        try:
            auctionuser = AuctionUser.objects.get(user=request.user)
            if auctionuser.status == "pending":
                messages.success(request, "Your verification is pending. Complete your additional detail and email verification. If these are already completed then try login after sometime. We are working on your detail verification. Thanks!")
        except AuctionUser.DoesNotExist:
            messages.warning(request, "Please complete your profile setup to continue.")

    upcoming_product = Product.objects.filter(status="upcoming")
    closed_product = Product.objects.filter(status="closed")
    live_product = Product.objects.filter(status="live")
    d = {'upcoming_product':upcoming_product, 'closed_product':closed_product, 'live_product':live_product}
    return render(request, 'home.html', d)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def signup(request):
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        con = request.POST['contact']
        add = request.POST['add']
        d2 = request.POST['dob']
        reg = request.POST['reg']
        i = request.FILES['image']
        user = User.objects.create_user(email=e, username=u, password=p, first_name=f,last_name=l)
        mem = Member_fee.objects.get(fee="Unpaid")
        sign = AuctionUser.objects.create(membership=mem,user=user,contact=con,address=add,dob=d2,image=i, user_type=reg)
        messages.success(request, "Registration Successfully")
        return redirect('home')
    return render(request, 'signup.html')

def Logout(request):
    logout(request)
    return redirect('home')

def login_user(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        
        if user is None:
            messages.error(request, "User not found. Please check your username.")
            return render(request, 'login.html')
            
        if not user.check_password(p):
            messages.error(request, "Incorrect password. Please try again.")
            return render(request, 'login.html')
            
        if user.is_staff:
            messages.error(request, "Please use the admin login page for admin access.")
            return render(request, 'login.html')
            
        try:
            auctionuser = AuctionUser.objects.get(user=user)
            if auctionuser.status == "pending":
                messages.warning(request, "Your profile is under review. Please wait for admin verification.")
                return render(request, 'login.html')
        except AuctionUser.DoesNotExist:
            messages.warning(request, "Please complete your profile setup first.")
            return render(request, 'login.html')
            
        login(request, user)
        messages.success(request, "Logged in successfully!")
        return redirect('home')
        
    return render(request, 'login.html')


def Add_Product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        auctionuser = AuctionUser.objects.get(user=request.user)
        if auctionuser.status == "pending":
            messages.success(request, "Your verification is pending. Complete your additional detail and email verification. If these are already completed then try login after sometime. We are working on your detail verification. Thanks!")
            return redirect('profile', request.user.id)
    except AuctionUser.DoesNotExist:
        messages.warning(request, "Please complete your profile setup to continue.")
        return redirect('profile', request.user.id)
    
    cat = Category.objects.all()
    if request.method == "POST":
        c = request.POST['cat']
        p = request.POST['p_name']
        pr = request.POST['price']
        im = request.FILES['image']
        start = request.POST['start']
        end = request.POST['interval_price']
        desc = request.POST['desc']
        cat_obj = Category.objects.get(id=c)
        pro1=Product.objects.create(description=desc, bid_type="Auction", status="pending",session=start, interval_price=end, category=cat_obj, name=p, min_price=pr, final_price=pr, images=im, user=request.user)
        messages.success(request, "Product added successfully.")
        return redirect('view_product')
    d = {'cat': cat}
    return render(request, 'add_product.html', d)


def edit_product(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    
    if request.user.is_authenticated:
        auctionuser = AuctionUser.objects.get(user=request.user)
        if auctionuser.status == "pending":
            messages.success(request, "Your verification is pending. complete your additional detail and email verification. if these are already completed then try login after sometime.We are working on your detail verification.Thanks!")
            return redirect('profile', request.user.id)
    data = Product.objects.get(id=pid)
    cat = Category.objects.all()
    if request.method=="POST":
        c = request.POST['cat']
        p = request.POST['p_name']
        pr = request.POST['price']
        start = request.POST['start']
        end = request.POST['interval_price']
        desc = request.POST['desc']
        try:
            i = request.FILES['image']
            data.images = i
            data.save()
        except:
            pass
        cat_obj = Category.objects.get(id=c)
        Product.objects.filter(id=pid).update(description=desc, bid_type="Auction", session=start, interval_price=end, category=cat_obj, name=p, min_price=pr, final_price=pr, user=request.user)
        messages.success(request, "Product Updated")
        return redirect('view_product')
    d = {'cat': cat, 'data':data}
    return render(request, 'edit_product.html', d)


def view_product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_authenticated:
        try:
            auctionuser = AuctionUser.objects.get(user=request.user)
            if auctionuser.status == "pending":
                messages.success(request, "Your verification is pending. Complete your additional detail and email verification. If these are already completed then try login after sometime. We are working on your detail verification. Thanks!")
        except AuctionUser.DoesNotExist:
            messages.warning(request, "Please complete your profile setup to continue.")
    product = Product.objects.filter(user=request.user)
    return render(request, 'view_product.html', {'product': product})


def delete_product(request,pid):
    if not request.user.is_authenticated:
        return redirect('login')
    pro = Product.objects.get(id=pid)
    pro.delete()
    messages.success(request, "Deleted Successfully")
    return redirect('view_product')

def product_detail(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_authenticated:
        auctionuser = AuctionUser.objects.get(user=request.user)
        if auctionuser.status == "pending":
            messages.success(request, "Your verification is pending. complete your additional detail and email verification. if these are already completed then try login after sometime.We are working on your detail verification.Thanks!")
            return redirect('profile', request.user.id)
    product = Product.objects.get(id=pid)
    return render(request, 'product_detail.html', {'product':product})

def make_participants(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        auctionuser = AuctionUser.objects.get(user=request.user)
        if auctionuser.status == "pending":
            messages.success(request, "Your verification is pending. Complete your additional detail and email verification. If these are already completed then try login after sometime. We are working on your detail verification. Thanks!")
            return redirect('profile', request.user.id)
    except AuctionUser.DoesNotExist:
        messages.warning(request, "Please complete your profile setup to continue.")
        return redirect('profile', request.user.id)
    
    try:
        product = Product.objects.get(id=pid)
        # Check if user is already a participant
        existing_participant = Participants.objects.filter(user=request.user, product=product).exists()
        if existing_participant:
            messages.warning(request, "You are already a participant in this auction.")
            return redirect('product_detail', pid)
            
        # Create new participant
        participant = Participants.objects.create(user=request.user, product=product)
        messages.success(request, "Successfully added as a participant.")
        return redirect('product_detail', pid)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('all_product')

def getbidhistory(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    product = Product.objects.get(id=pid)
    participant = ParticipantsHistory.objects.filter(product=product).order_by('-id')[:5]
    winner_status = False
    if product.bid_type == "Tendor":
        max_val = product.min_price-product.interval_price
    else:
        max_val = product.min_price+product.interval_price

    if participant.first():
        minutes = datetime.now(timezone.utc) - participant.first().created
        
        if minutes.seconds/60 >= 5 and product.status == "live":
            product.winner = participant.first().user
            product.status = "closed"
            winner_status = True

        
        if product.bid_type == "Tendor":
            max_val = participant.first().new_price-product.interval_price
        else:
            max_val = participant.first().new_price+product.interval_price

    d = {'status':'Success', 'new_price':[], 'name':[], 'time':[], 'maximum':max_val, 'winner_status':winner_status}
    try:
        product.final_price = participant.first().new_price
        product.save()
    except:
        pass
    for i in participant:
        d['new_price'].append(i.new_price)
        d['name'].append(i.user.first_name+" "+i.user.last_name)
        d['time'].append(i.created)
    return JsonResponse(d)

def startbidding(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    
    product = Product.objects.get(id=pid)
    participant1 = ParticipantsHistory.objects.filter(product=product).order_by('-id')[:5]
    new = request.POST.get('new_price')
    
    winner_status = False
    if participant1.first():
        minutes = datetime.now(timezone.utc) - participant1.first().created
        if minutes.seconds/60 >= 5 and product.status == "live":
            product.winner = participant.first().user
            product.status = "closed"
            product.save()
            messages.success(request, "Sorry! You are late, Winner has announced.")
        else:
            participant = ParticipantsHistory.objects.create(user=request.user, product=product, new_price=new)
    else:
        participant = ParticipantsHistory.objects.create(user=request.user, product=product, new_price=new)
    return redirect('product_detail', pid)

def changelivetocomplete(request, pid):
    product = Product.objects.get(id=pid)
    winner = ParticipantsHistory.objects.filter(product=product).last()
    product.status = "closed"
    
    response_data = {'myurl': '/'}
    
    if winner:
        product.winner = winner.user
        
        # Add winner and seller details to response
        if request.user == winner.user:
            response_data.update({
                'is_winner': True,
                'seller_name': f"{product.user.first_name} {product.user.last_name}",
                'seller_contact': product.user.auctionuser_set.first().contact,
                'final_price': str(product.final_price)
            })
        elif request.user == product.user:
            response_data.update({
                'is_seller': True,
                'winner_name': f"{winner.user.first_name} {winner.user.last_name}",
                'winner_contact': winner.user.auctionuser_set.first().contact
            })
    
    product.save()
    return JsonResponse(response_data)

def changeupcomingtolive(request, pid):
    product = Product.objects.get(id=pid)
    winner = ParticipantsHistory.objects.filter(product=product).last()
    product.status = "live"
    product.save()
    return JsonResponse({'myurl':'/'})

def meetwinners(request):
    if request.user.is_authenticated:
        try:
            auctionuser = AuctionUser.objects.get(user=request.user)
            if auctionuser.status == "pending":
                messages.success(request, "Your verification is pending. Complete your additional detail and email verification. If these are already completed then try login after sometime. We are working on your detail verification. Thanks!")
        except AuctionUser.DoesNotExist:
            messages.warning(request, "Please complete your profile setup to continue.")
    product = Product.objects.filter().exclude(winner=None)
    return render(request, 'meetwinners.html', {'product':product})


def all_product(request):
    if request.user.is_authenticated:
        try:
            auctionuser = AuctionUser.objects.get(user=request.user)
            if auctionuser.status == "pending":
                messages.success(request, "Your verification is pending. Complete your additional detail and email verification. If these are already completed then try login after sometime. We are working on your detail verification. Thanks!")
        except AuctionUser.DoesNotExist:
            messages.warning(request, "Please complete your profile setup to continue.")
    product = Product.objects.filter().exclude(status="pending")
    return render(request, 'HotProducts.html', {'product':product})


def admin_home(request):
    bidder = AuctionUser.objects.filter(user_type="Bidder")
    seller = AuctionUser.objects.filter(user_type="Seller")
    auction = Product.objects.filter(bid_type="Auction")
    d = {'bidder':bidder.count(), 'seller':seller.count(), 'auction':auction.count()}
    return render(request, 'administration/admin_home.html', d)


def Admin_Login(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                messages.success(request, "Logged in Successfully")
                return redirect('admin_home')
            else:
                messages.success(request, "Invalid Credentials.")
        except:
            messages.success(request, "Invalid Credentials.")
    return render(request,'administration/loginadmin.html')


def view_seller_user(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    sellers = AuctionUser.objects.filter(user_type='Seller')
    return render(request, 'administration/view_user.html', {'data': sellers})


def view_buyer_user(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    buyers = AuctionUser.objects.filter(user_type="Bidder")
    return render(request, 'administration/view_user.html', {'data': buyers})



def view_participants(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    pro = Participants.objects.filter()
    d = {'pro':pro}
    return render(request,'administration/view_participants.html',d)


def Admin_product(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    product = Product.objects.filter()
    d ={'pro':product}
    return render(request,'administration/admin_view_product.html',d)


def Add_Category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.FILES.get('icon')
        description = request.POST.get('description')
        
        category = Category.objects.create(
            name=name,
            icon=icon,
            description=description
        )
        return redirect('view_category')
    return render(request, 'administration/add_category.html')


def View_Category(request):
    categories = Category.objects.all()
    return render(request, 'administration/view_category.html', {'categories': categories})


def Delete_Category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('view_category')


def view_winner(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    pro = Product.objects.filter().exclude(winner=None)
    d = {'pro': pro}
    return render(request,'administration/view_winner.html', d)



def delete_admin_product(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    pro = Product.objects.get(id=pid)
    pro.delete()
    messages.success(request, "Deleted Successfully")
    return redirect('admin_view_product')


def delete_category(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    cat = Category.objects.get(id=pid)
    cat.delete()
    messages.success(request, "Deleted Successfully")
    return redirect('view_categary')


def delete_user(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    cat = User.objects.get(id=pid)
    cat.delete()
    messages.success(request, "Deleted Successfully")
    return redirect('view_buyer_user')


def delete_participant(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    participant = Participants.objects.get(id=pid)
    participant.delete()
    messages.success(request, "Deleted Successfully")
    return redirect('view_participants')


def change_status(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    cat = Product.objects.get(id=pid)
    cat.status = "upcoming"
    cat.save()
    messages.success(request, "Status Changed Successfully")
    return redirect('admin_view_product')


def change_user_status(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    cat = AuctionUser.objects.get(id=pid)
    if cat.status == "Approved":
        cat.status = "pending"
    else:
        cat.status = "Approved"
    cat.save()
    messages.success(request, "Status Changed Successfully")
    if cat.user_type == "Seller":
        return redirect('view_seller_user')
    else:
        return redirect('view_buyer_user')


def Change_Password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            messages.success(request, "Changed Successfully")
        else:
            messages.success(request, "Password not matching")
    if request.user.is_staff:
        return render(request, 'administration/change_password.html', )
    else:
        return render(request,'change_password.html')


def profile(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user = User.objects.get(id=pid)
        try:
            pro = AuctionUser.objects.get(user=user)
            d = {'pro': pro, 'user': user}
            return render(request, 'profile.html', d)
        except AuctionUser.DoesNotExist:
            messages.error(request, "User profile not found. Please complete your profile setup.")
            return redirect('signup')
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('home')


def Edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    pro = AuctionUser.objects.get(user=request.user)
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        ad = request.POST['add']
        e = request.POST['email']
        con = request.POST['contact']
        d = request.POST['date']
        acn = request.POST['account_number']

        try:
            i = request.FILES['img']
            pro.image = i
            pro.save()
        except:
            pass

        try:
            bs = request.FILES['bank_statement']
            pro.bank_statement = bs
            pro.save()
        except:
            pass

        pro.dob = d
        pro.user.username = u
        pro.user.first_name = f
        pro.user.last_name = l
        pro.user.email = e
        pro.contact = con
        pro.address = ad
        pro.account_number = acn
        pro.save()
        pro.user.save()
        messages.success(request, "Updated Successfully")
        return redirect('profile', request.user.id)
    d = {'pro':pro}
    return render(request, 'edit_profile.html',d)

def email_verify(request, pid):
    user = AuctionUser.objects.get(id=pid)
    if request.method == "POST":
        otp = request.POST['otp']
        if user.otp == str(otp):
            user.email_verification = True
            user.save()
            messages.success(request, "Email Varified Successfully")
            return redirect('profile', user.user.id)
        else:
            messages.success(request, "Invalid OTP.")
            return redirect('email_verify', pid)
    return render(request, 'verify_email.html',{'pid':pid})
    

def generateotp(request, pid):
    user = AuctionUser.objects.get(id=pid)
    digits = [i for i in range(0, 10)]
    random_str = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    email_host = settings.EMAIL_HOST_USER
    print(user.user.email)
    html_content = "<h4>Your Email Verification code is : </h4><h3>"+str(random_str)+"</h3>"
    email = EmailMessage("Send Verification Code", html_content, str(email_host), [str(user.user.email),])
    email.content_subtype = "html"
    res = email.send()
    user.otp = random_str
    user.save()
    return JsonResponse({'Success':True})

def admin_product_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    product = Product.objects.get(id=pid)
    if request.method == "POST":
        comment = request.POST['comment']
        product.comment = comment
        product.save()
        messages.success(request, "Commented Successfully")
        return redirect('admin_product_detail', pid)
    d = {'product':product, 'booking_id':pid}
    return render(request,'administration/admin_product_detail.html',d)

def bidder_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    data = AuctionUser.objects.get(id=pid)
    d = {'data':data}
    return render(request,'administration/bidder_detail.html',d)

def seller_detail(request,pid):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    data = AuctionUser.objects.get(id=pid)
    d = {'data':data}
    return render(request,'administration/seller_detail.html',d)
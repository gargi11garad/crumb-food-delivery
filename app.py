import os
import requests
import streamlit as st

st.set_page_config(page_title="crumb · neighborhood food", page_icon="🥑", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Playfair+Display:ital,wght@0,500;1,600&display=swap');
.stApp{background:#fbf9f3;color:#20251f}.block-container{max-width:1180px;padding-top:2rem}.hero{padding:38px 42px;background:#e8eddf;border-radius:12px;margin-bottom:26px}.hero h1{font:56px 'Playfair Display';line-height:1.05;margin:8px 0}.hero em{color:#758c55}.muted{color:#74776f}.menuitem{background:#fff;border:1px solid #eeece4;border-radius:9px;padding:18px;margin:5px 0 15px}.price{font-weight:700;color:#314c3c}.stButton button{border-radius:6px}
</style>""", unsafe_allow_html=True)
API=os.getenv("API_URL", "http://localhost:4000").rstrip("/")
@st.cache_data(ttl=45)
def load_restaurants(q=""):
    try:
        r=requests.get(API+"/api/restaurants",params={"q":q},timeout=4);r.raise_for_status();return r.json(),None
    except Exception as e:
        return [{"_id":"1","name":"Juniper & Rye","cuisine":"Seasonal bowls · New American","featuredDish":"Harvest grain bowl","price":15,"emoji":"🥑","rating":4.9,"description":"Warm farro, roasted squash, whipped feta, crispy sage & maple."},{"_id":"2","name":"Little Napoli","cuisine":"Wood-fired pizza · Italian","featuredDish":"Hot honey margherita","price":18,"emoji":"🍕","rating":4.8,"description":"San Marzano tomato, fior di latte, basil and hot honey."},{"_id":"3","name":"Momo House","cuisine":"Dumplings · Asian comfort","featuredDish":"Crispy chili momos","price":13,"emoji":"🥟","rating":4.9,"description":"Hand-folded dumplings, black vinegar and house chili crunch."}],str(e)
st.markdown('<div class="hero"><div>✳ &nbsp; GOOD FOOD, RIGHT AROUND THE CORNER</div><h1>Find your kind of <em>delicious.</em></h1><div class="muted">The neighborhood’s best, brought to your door. Made with care.</div></div>',unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## 🥡 crumb")
    st.caption("Good food, good mood.")
    page=st.radio("Your table",["Discover","Your bag","Order history","Restaurant & order dashboard"],label_visibility="collapsed")
    st.divider();st.caption("Streamlit edition · Connect an API with API_URL")
if page=="Discover":
    q=st.text_input("Search dishes and kitchens",placeholder="Try dumplings, pizza, brunch…")
    rows,err=load_restaurants(q)
    if err: st.info("Showing sample kitchens. Set API_URL to connect the Express API.")
    if "cart" not in st.session_state: st.session_state.cart={}
    cols=st.columns(3)
    for idx,r in enumerate(rows):
        with cols[idx%3]:
            st.markdown(f'<div class="menuitem"><div style="font-size:48px">{r.get("emoji","🍽️")}</div><h3>{r["name"]}</h3><div class="muted">⭐ {r.get("rating",4.8)} · {r.get("cuisine","")}</div><p><b>{r.get("featuredDish","")}</b><br><span class="muted">{r.get("description","")}</span></p><span class="price">${r.get("price",0):.2f}</span></div>',unsafe_allow_html=True)
            if st.button("＋ Add to bag",key="add_"+str(r["_id"]),use_container_width=True):
                ident=str(r["_id"]);st.session_state.cart[ident]=st.session_state.cart.get(ident,{"restaurantId":ident,"name":r.get("featuredDish",r["name"]),"price":r.get("price",0),"quantity":0});st.session_state.cart[ident]["quantity"]+=1;st.toast("Added to your bag");st.rerun()
elif page=="Your bag":
    cart=st.session_state.get("cart",{});st.title("Your bag")
    if not cart: st.info("Your bag is waiting on the good stuff.")
    else:
        for k,item in list(cart.items()):
            c1,c2,c3=st.columns([5,1,1]);c1.write(f"**{item['name']}** · ${item['price']:.2f}");c2.write(f"× {item['quantity']}")
            if c3.button("Remove",key="rm"+k): del cart[k];st.rerun()
        total=sum(i["price"]*i["quantity"] for i in cart.values());st.subheader(f"Subtotal · ${total:.2f}")
        token=st.session_state.get("token")
        if st.button("Place your order",type="primary"):
            if token:
                try:
                    res=requests.post(API+"/api/orders",json={"items":list(cart.values())},headers={"Authorization":"Bearer "+token},timeout=10);res.raise_for_status();st.session_state.cart={};st.success("Order placed! Your kitchen is on it.")
                except Exception as e: st.error(f"Order could not be placed: {e}")
            else:
                if "demo_orders" not in st.session_state: st.session_state.demo_orders=[]
                st.session_state.demo_orders.insert(0,{"status":"Received","total":total,"items":list(cart.values())})
                st.session_state.cart={};st.success("Order placed! Your kitchen is on it.");st.rerun()
elif page=="Order history":
    st.title("Order history")
    if not st.session_state.get("token"):
        orders=st.session_state.get("demo_orders",[])
        if not orders: st.info("Your next favorite is out there.")
        for o in orders: st.markdown(f"**{o.get('status','Received')}** · ${o.get('total',0):.2f} · {len(o.get('items',[]))} items")
    else:
        try:
            orders=requests.get(API+"/api/orders/mine",headers={"Authorization":"Bearer "+st.session_state.token},timeout=5).json()
            if not orders: st.info("Your next favorite is out there.")
            for o in orders: st.markdown(f"**{o.get('status','Received')}** · ${o.get('total',0):.2f} · {len(o.get('items',[]))} items")
        except Exception as e: st.error(str(e))
else:
    st.title("Restaurant & order dashboard")
    with st.expander("Staff sign in",expanded=not bool(st.session_state.get("token"))):
        with st.form("login"):
            email=st.text_input("Email");password=st.text_input("Password",type="password");submit=st.form_submit_button("Sign in")
            if submit:
                try:
                    r=requests.post(API+"/api/auth/login",json={"email":email,"password":password},timeout=5);r.raise_for_status();st.session_state.token=r.json()["token"];st.success("Signed in")
                except Exception: st.error("Unable to sign in. Check your account and API URL.")
    if st.session_state.get("token"):
        try:
            orders=requests.get(API+"/api/admin/orders",headers={"Authorization":"Bearer "+st.session_state.token},timeout=5);orders.raise_for_status()
            for order in orders.json(): st.write(f"Order {str(order['_id'])[-6:]} · ${order['total']:.2f} · {order['status']}")
        except Exception: st.caption("Sign in with an admin account to manage orders. The API restricts this view to admin roles.")
    with st.expander("Create an account"):
        with st.form("register"):
            name=st.text_input("Name");email=st.text_input("Email address",key="new_email");password=st.text_input("Password (8+ characters)",type="password",key="new_password")
            if st.form_submit_button("Create account"):
                try:
                    r=requests.post(API+"/api/auth/register",json={"name":name,"email":email,"password":password},timeout=5);r.raise_for_status();st.session_state.token=r.json()["token"];st.success("Account created")
                except Exception as e: st.error(f"Could not create account: {e}")

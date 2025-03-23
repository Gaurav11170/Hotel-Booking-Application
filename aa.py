import streamlit as st
import pandas as pd
import datetime
import smtplib
from email.mime.text import MIMEText
import random
import string
import os

# Email Configuration
SENDER_EMAIL = "patilgaurav075@gmail.com"
EMAIL_APP_PASSWORD = "pxno vshc pzbe xezs"

BOOKING_FILE = 'booking.csv'

def load_data():
    """Load and process hotel and location data"""
    hotels_df = pd.read_csv('hotels.csv')
    north_df = pd.read_csv('north.csv')
    south_df = pd.read_csv('south.csv')

    # Clean price column
    hotels_df['Price'] = hotels_df['Price'].astype(str)
    hotels_df['Price'] = hotels_df['Price'].apply(lambda x: ''.join(filter(str.isdigit, x)))
    hotels_df['Price'] = pd.to_numeric(hotels_df['Price'], errors='coerce')

    return hotels_df, north_df, south_df

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_email(receiver_email, subject, message):
    """Send email using SMTP"""
    try:
        msg = MIMEText(message)
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def send_otp_email(email, otp):
    """Send OTP for email verification"""
    subject = "Email Verification OTP"
    message = f"Your OTP for email verification is: {otp}\n\nThis OTP will expire in 10 minutes."
    return send_email(email, subject, message)

def save_booking(data):
    """Save booking details to CSV"""
    if os.path.exists(BOOKING_FILE):
        df = pd.read_csv(BOOKING_FILE)
    else:
        df = pd.DataFrame(columns=data.keys())  # Create empty DataFrame with the same columns

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)  # Correct way to append
    df.to_csv(BOOKING_FILE, index=False)

def display_dashboard():
    """Display hotel search and filtering"""
    st.header("🏨 Hotel Search Dashboard")
    hotels_df, north_df, south_df = load_data()

    all_locations = pd.concat([
        north_df[['State_UT', 'Places']],
        south_df[['State_UT', 'Places']]
    ]).drop_duplicates()

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_state = st.selectbox("Select State/UT", ['All'] + sorted(all_locations['State_UT'].unique().tolist()))

    available_places = all_locations[all_locations['State_UT'] == selected_state]['Places'].tolist() if selected_state != 'All' else all_locations['Places'].tolist()

    with col2:
        selected_place = st.selectbox("Select Destination", ['All'] + sorted(available_places))

    with col3:
        price_range = st.slider("Price Range (₹)", int(hotels_df['Price'].min()), int(hotels_df['Price'].max()),
                                (int(hotels_df['Price'].min()), int(hotels_df['Price'].max())))

    filtered_hotels = hotels_df.copy()
    if selected_place != 'All':
        filtered_hotels = filtered_hotels[filtered_hotels['Places'] == selected_place]
    filtered_hotels = filtered_hotels[(filtered_hotels['Price'] >= price_range[0]) & (filtered_hotels['Price'] <= price_range[1])]

    st.subheader(f"Available Hotels ({len(filtered_hotels)} results)")

    cols = st.columns(3)
    for idx, hotel in filtered_hotels.iterrows():
        col_idx = idx % 3
        with cols[col_idx]:
            st.markdown(f"**{hotel['Name']}**\n📍 {hotel['Places']}\n⭐ {hotel['Category']}\n💰 ₹{hotel['Price']:,.0f} per night")
            if st.button(f"Book Now 🏷️", key=f"book_{idx}"):
                st.session_state.selected_hotel = hotel
                st.session_state.show_booking_form = True
                st.rerun()

def display_booking_form():
    """Display booking form"""
    hotel = st.session_state.selected_hotel

    st.header(f"Book Your Stay at {hotel['Name']}")
    st.subheader(f"📍 {hotel['Places']} | ⭐ {hotel['Category']} | 💰 ₹{hotel['Price']:,.0f} per night")

    with st.form(key='booking_form', clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input('First Name*')
            email = st.text_input('Email*')
            check_in = st.date_input('Check-in Date*')

        with col2:
            last_name = st.text_input('Last Name*')
            phone = st.text_input('Phone Number*')
            check_out = st.date_input('Check-out Date*', min_value=check_in)

        guests = st.number_input('Number of Guests*', min_value=1, max_value=10, value=1)
        terms = st.checkbox('I agree to the terms and conditions*')

        submitted = st.form_submit_button('Submit Booking')
        if submitted and all([first_name, last_name, email, phone, terms]):
            process_booking(first_name, last_name, email, phone, check_in, check_out, guests, hotel)

def process_booking(first_name, last_name, email, phone, check_in, check_out, guests, hotel):
    """Process booking"""
    duration = (check_out - check_in).days
    otp = generate_otp()

    booking_data = {
        'FirstName': first_name, 'LastName': last_name, 'Email': email, 'Phone': phone,
        'Hotel': hotel['Name'], 'Location': hotel['Places'], 'Category': hotel['Category'],
        'Price': hotel['Price'], 'CheckIn': check_in.strftime('%Y-%m-%d'), 'CheckOut': check_out.strftime('%Y-%m-%d'),
        'Duration': f"{duration} days", 'Guests': guests, 'OTP': otp, 'BookingTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_booking(booking_data)
    send_otp_email(email, otp)

    st.success('Booking submitted! Check your email for OTP to view details.')

def view_booking():
    """View booking using OTP"""
    st.title('🔍 View Your Booking')

    with st.form(key='view_booking_form'):
        otp = st.text_input('Enter your OTP')
        submit_view = st.form_submit_button('View Booking')

        if submit_view and otp:
            if os.path.exists(BOOKING_FILE):
                bookings = pd.read_csv(BOOKING_FILE)
                user_booking = bookings[bookings['OTP'] == otp]

                if not user_booking.empty:
                    st.dataframe(user_booking)
                else:
                    st.warning('No booking found with this OTP.')
            else:
                st.warning('No bookings found.')

def reset_session_state():
    """Reset all session state variables"""
    st.session_state.show_booking_form = False
    st.session_state.selected_hotel = None
    st.session_state.booking_data = None
    st.session_state.show_review = False
    st.rerun()

def main():
    st.set_page_config(page_title='Hotel Booking', layout='wide')

    with st.sidebar:
        st.button('Reset', on_click=reset_session_state)

    option = st.sidebar.radio("Navigation", ["Home", "View Booking"])

    if option == "Home":
        if not st.session_state.get("show_booking_form", False):
            display_dashboard()
        else:
            display_booking_form()
    else:
        view_booking()

if __name__ == "__main__":
    main()

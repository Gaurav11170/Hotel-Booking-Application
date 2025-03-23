import streamlit as st
import pandas as pd
import datetime
import smtplib
from email.mime.text import MIMEText
import random
import string
import os

# Email configuration
SENDER_EMAIL = "anithatechnologiesandservices@gmail.com"
EMAIL_APP_PASSWORD = "pxno vshc pzbe xezs"

# File paths
BOOKING_FILE = 'booking.csv'
HOTELS_FILE = 'hotels.csv'
NORTH_FILE = 'north.csv'
SOUTH_FILE = 'south.csv'

def ensure_file_exists(filename, columns):
    """Ensure file exists and create with headers if it doesn't"""
    try:
        if not os.path.exists(filename):
            df = pd.DataFrame(columns=columns)
            df.to_csv(filename, index=False)
    except Exception as e:
        st.error(f"Error creating file {filename}: {str(e)}")

def load_data():
    """Load and process hotel and location data"""
    try:
        hotels_df = pd.read_csv(HOTELS_FILE)
        north_df = pd.read_csv(NORTH_FILE)
        south_df = pd.read_csv(SOUTH_FILE)
        
        # Clean price column
        hotels_df['Price'] = hotels_df['Price'].astype(str)
        hotels_df['Price'] = hotels_df['Price'].apply(lambda x: ''.join(filter(str.isdigit, x)))
        hotels_df['Price'] = pd.to_numeric(hotels_df['Price'], errors='coerce')
        
        return hotels_df, north_df, south_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def load_bookings():
    """Load booking data"""
    booking_columns = ['OTP', 'Firstname', 'Secondname', 'Place_ID', 'Duration', 
                      'Total_Members', 'Date_time', 'Hotel']
    ensure_file_exists(BOOKING_FILE, booking_columns)
    
    try:
        return pd.read_csv(BOOKING_FILE)
    except Exception as e:
        st.error(f"Error loading bookings: {str(e)}")
        return pd.DataFrame(columns=booking_columns)

def save_booking(booking_data):
    """Save booking to CSV file"""
    try:
        bookings_df = load_bookings()
        new_booking = pd.DataFrame([booking_data])
        updated_bookings = pd.concat([bookings_df, new_booking], ignore_index=True)
        updated_bookings.to_csv(BOOKING_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving booking: {str(e)}")
        return False

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_email(receiver_email, subject, message):
    """Helper function to send emails"""
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
    """Send OTP via email"""
    subject = "Email Verification OTP"
    message = f"""
    Your OTP for email verification is: {otp}
    
    This OTP will expire in 10 minutes.
    Please do not share this OTP with anyone.
    """
    return send_email(email, subject, message)

def reset_session_state():
    """Reset all session state variables"""
    for key in ['show_booking_form', 'selected_hotel', 'booking_data', 'show_review',
                'otp', 'email_verified', 'verification_email', 'otp_sent', 'view_bookings']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def view_bookings():
    """Display the view bookings page"""
    st.title('View Your Booking')
    
    with st.form(key='view_booking_form'):
        otp = st.text_input('Enter your OTP')
        submit_view = st.form_submit_button('View Booking')
        
        if submit_view and otp:
            bookings = load_bookings()
            user_booking = bookings[bookings['OTP'].astype(str) == otp]
            
            if not user_booking.empty:
                st.success("Booking found!")
                st.dataframe(user_booking)
            else:
                st.warning('No booking found with this OTP.')

def display_dashboard():
    """Display the hotel search and filtering dashboard"""
    st.header("🏨 Hotel Search Dashboard")
    
    # Load data
    hotels_df, north_df, south_df = load_data()
    if hotels_df is None:
        return
    
    # Combine location data
    all_locations = pd.concat([
        north_df[['State_UT', 'Places']],
        south_df[['State_UT', 'Places']]
    ]).drop_duplicates()
    
    # Create filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_state = st.selectbox(
            "Select State/UT",
            options=['All'] + sorted(all_locations['State_UT'].unique().tolist())
        )
    
    # Filter locations based on selected state
    if selected_state != 'All':
        available_places = all_locations[all_locations['State_UT'] == selected_state]['Places'].tolist()
    else:
        available_places = all_locations['Places'].tolist()
    
    with col2:
        selected_place = st.selectbox(
            "Select Destination",
            options=['All'] + sorted(available_places)
        )
    
    with col3:
        price_range = st.slider(
            "Price Range (₹)",
            min_value=int(hotels_df['Price'].min()),
            max_value=int(hotels_df['Price'].max()),
            value=(int(hotels_df['Price'].min()), int(hotels_df['Price'].max()))
        )
    
    # Filter hotels
    filtered_hotels = hotels_df.copy()
    if selected_place != 'All':
        filtered_hotels = filtered_hotels[filtered_hotels['Places'] == selected_place]
    filtered_hotels = filtered_hotels[
        (filtered_hotels['Price'] >= price_range[0]) &
        (filtered_hotels['Price'] <= price_range[1])
    ]
    
    # Display results
    st.subheader(f"Available Hotels ({len(filtered_hotels)} results)")
    
    # Display hotels in a grid
    cols = st.columns(3)
    for idx, hotel in filtered_hotels.iterrows():
        col_idx = idx % 3
        with cols[col_idx]:
            st.markdown(f"""
            **{hotel['Name']}**  
            📍 {hotel['Places']}  
            ⭐ {hotel['Category']}  
            💰 ₹{hotel['Price']:,.0f} per night
            """)
            if st.button(f"Book Now 🏷️", key=f"book_{idx}"):
                st.session_state.selected_hotel = hotel
                st.session_state.show_booking_form = True
                st.rerun()

def verify_email():
    """Handle email verification process"""
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
        
    if not st.session_state.otp_sent:
        email = st.text_input('Email*')
        if st.button('Send OTP'):
            if email:
                otp = generate_otp()
                if send_otp_email(email, otp):
                    st.session_state.verification_email = email
                    st.session_state.otp = otp
                    st.session_state.otp_sent = True
                    st.success('OTP sent successfully!')
                    st.rerun()
            else:
                st.error('Please enter your email address.')
    else:
        entered_otp = st.text_input('Enter OTP*')
        if st.button('Verify OTP'):
            if entered_otp == st.session_state.otp:
                st.session_state.email_verified = True
                st.success('Email verified successfully!')
                st.rerun()
            else:
                st.error('Invalid OTP. Please try again.')

def display_booking_form():
    """Display the booking form for the selected hotel"""
    hotel = st.session_state.selected_hotel
    
    st.header(f"Book Your Stay at {hotel['Name']}")
    st.subheader(f"📍 {hotel['Places']} | ⭐ {hotel['Category']} | 💰 ₹{hotel['Price']:,.0f} per night")
    
    # First verify email if not already verified
    if not st.session_state.get('email_verified', False):
        verify_email()
        return
    
    with st.form(key='booking_form', clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input('First Name*')
            phone = st.text_input('Phone Number*')
            check_in = st.date_input('Check-in Date*')
        
        with col2:
            last_name = st.text_input('Last Name*')
            check_out = st.date_input('Check-out Date*', min_value=check_in)
        
        guests = st.number_input('Number of Guests*', min_value=1, max_value=10, value=1)
        special_requests = st.text_area('Special Requests', height=100)
        terms = st.checkbox('I agree to the terms and conditions*')
        
        submitted = st.form_submit_button('Submit Booking', use_container_width=True)
        
        if submitted:
            process_booking(
                first_name, last_name, 
                st.session_state.verification_email, 
                phone, check_in, check_out, 
                guests, special_requests, terms, hotel
            )

def process_booking(first_name, last_name, email, phone, check_in, check_out, guests, special_requests, terms, hotel):
    """Process the booking submission"""
    if all([first_name, last_name, phone, terms]):
        duration = (check_out - check_in).days
        otp = generate_otp()
        
        booking_data = {
            'OTP': otp,
            'Firstname': first_name,
            'Secondname': last_name,
            'Place_ID': hotel['Places'],
            'Duration': f"{duration} days",
            'Total_Members': guests,
            'Date_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Hotel': hotel['Name']
        }
        
        # Save booking data
        if save_booking(booking_data):
            st.session_state.booking_data = {
                **booking_data,
                'Email': email,
                'Phone': phone,
                'CheckIn': check_in.strftime('%Y-%m-%d'),
                'CheckOut': check_out.strftime('%Y-%m-%d'),
                'SpecialRequests': special_requests,
                'Category': hotel['Category'],
                'Price': hotel['Price']
            }
            
            # Send booking confirmation email
            subject = "Booking Confirmation"
            message = f"""
            Thank you for your booking!
            
            Booking Details:
            Hotel: {hotel['Name']}
            Check-in: {check_in}
            Check-out: {check_out}
            Duration: {duration} days
            Guests: {guests}
            
            Your booking OTP is: {otp}
            Please save this OTP to view your booking later.
            """
            
            if send_email(email, subject, message):
                st.success(f'Booking confirmed! Your OTP is: {otp}')
                st.info('Please save this OTP to view your booking later.')
                st.session_state.show_review = True
                st.rerun()
            else:
                st.error('Failed to send confirmation email. Please try again.')
        else:
            st.error('Failed to save booking. Please try again.')
    else:
        st.error('Please fill in all required fields and accept the terms.')

def main():
    st.set_page_config(page_title='Hotel Booking', layout='wide')
    
    # Initialize session state
    if 'show_booking_form' not in st.session_state:
        st.session_state.show_booking_form = False
    if 'selected_hotel' not in st.session_state:
        st.session_state.selected_hotel = None
    if 'booking_data' not in st.session_state:
        st.session_state.booking_data = None
    if 'show_review' not in st.session_state:
        st.session_state.show_review = False
    
    # Sidebar
    with st.sidebar:
        st.title('Navigation')
        if st.button('Reset'):
            reset_session_state()
        if st.button('View Bookings'):
            st.session_state.show_booking_form = False
            st.session_state.show_review = False
            st.session_state.view_bookings = True
            st.rerun()
    
    # Main content
    st.title('🏨 Luxury Hotels & Resorts Booking')
    
    if st.session_state.get('view_bookings', False):
        view_bookings()
    elif not st.session_state.show_booking_form:
        display_dashboard()
    elif st.session_state.show_review:
        st.success('Booking confirmed! Check your email for details.')
        if st.button('Make Another Booking'):
            reset_session_state()
    else:
        if st.button('← Back to Search'):
            st.session_state.show_booking_form = False
            st.rerun()
        display_booking_form()

if __name__ == "__main__":
    main()

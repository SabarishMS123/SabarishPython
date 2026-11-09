# HealthBot - Python GUI Application with Tkinter, PostgreSQL, Groq AI
# Requirements:
# pip install customtkinter psycopg2-binary bcrypt groq pillow requests geopy
# For verification: You'll need Twilio/SMS and email service (e.g., SendGrid). Placeholders provided.
# Set environment variables: GROQ_API_KEY, DATABASE_URL or hardcode DB creds (not recommended)
# For location: User inputs city or use geopy for coords.

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import os
from groq import Groq
import json
from datetime import datetime
import threading
import requests  # For hospital search (placeholder)

# ================== CONFIG ==================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")  # Replace or set env
DB_CONFIG = {
    "dbname": "healthbot",
    "user": "postgres",
    "password": "1522",
    "host": "localhost",
    "port": "5432"
}

# ================== DATABASE SETUP ==================
def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        title TEXT,
        messages JSONB,
        is_pinned BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# ================== AUTH FUNCTIONS ==================
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def register_user(name, email, password, phone):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        password_hash = hash_password(password)
        cur.execute("""
        INSERT INTO users (name, email, password_hash, phone)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """, (name, email, password_hash, phone))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        # TODO: Send verification email and SMS OTP here
        messagebox.showinfo("Success", "Registered! Verification pending (implement OTP).")
        return user_id
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

def login_user(email, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and verify_password(user['password_hash'], password):
            if not user['verified']:
                messagebox.showwarning("Warning", "Please verify your email/phone.")
            return user
        return None
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

# ================== CHAT FUNCTIONS ==================
client = Groq(api_key=GROQ_API_KEY)

def get_ai_response(user_query, history=None):
    messages = [{"role": "system", "content": """You are a helpful HealthBot. 
    Analyze symptoms for possible diseases (with disclaimers: not medical advice, consult doctor).
    Suggest priority treatments in a markdown table/chart.
    For hospitals: Suggest top ones near user location (user will provide city).
    Be empathetic, accurate, and safe."""}]
    
    if history:
        messages.extend(history[-10:])  # Last 10 messages
    
    messages.append({"role": "user", "content": user_query})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or mixtral, etc.
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def search_hospitals(city):
    # Placeholder - Integrate Google Places API or similar
    return f"Top hospitals in {city}: 1. Apollo Hospitals, 2. AIIMS, etc. (Use real API for production)."

# ================== GUI ==================
class HealthBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HealthBot - AI Health Assistant")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_user = None
        self.current_chat_id = None
        self.chat_history = []
        
        self.create_login_frame()
        
    def create_login_frame(self):
        self.clear_frames()
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.login_frame, text="HealthBot Login", font=ctk.CTkFont(size=24)).pack(pady=20)
        
        self.email_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Email")
        self.email_entry.pack(pady=10)
        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=10)
        
        ctk.CTkButton(self.login_frame, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Register", command=self.show_register).pack(pady=5)
        
    def show_register(self):
        self.clear_frames()
        self.reg_frame = ctk.CTkFrame(self)
        self.reg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.reg_frame, text="Register", font=ctk.CTkFont(size=24)).pack(pady=20)
        
        self.reg_name = ctk.CTkEntry(self.reg_frame, placeholder_text="Full Name")
        self.reg_name.pack(pady=5)
        self.reg_email = ctk.CTkEntry(self.reg_frame, placeholder_text="Email")
        self.reg_email.pack(pady=5)
        self.reg_phone = ctk.CTkEntry(self.reg_frame, placeholder_text="Phone")
        self.reg_phone.pack(pady=5)
        self.reg_pass = ctk.CTkEntry(self.reg_frame, placeholder_text="Password", show="*")
        self.reg_pass.pack(pady=5)
        
        ctk.CTkButton(self.reg_frame, text="Register", command=self.do_register).pack(pady=20)
        ctk.CTkButton(self.reg_frame, text="Back to Login", command=self.create_login_frame).pack()
        
    def do_register(self):
        name = self.reg_name.get()
        email = self.reg_email.get()
        phone = self.reg_phone.get()
        password = self.reg_pass.get()
        if name and email and phone and password:
            user_id = register_user(name, email, password, phone)
            if user_id:
                self.create_login_frame()
        else:
            messagebox.showwarning("Warning", "All fields required")
    
    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        user = login_user(email, password)
        if user:
            self.current_user = user
            self.load_main_ui()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def clear_frames(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def load_main_ui(self):
        self.clear_frames()
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        # Sidebar for chats
        self.sidebar = ctk.CTkFrame(self.main_frame, width=250)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text=f"Welcome, {self.current_user['name']}", font=ctk.CTkFont(size=16)).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="New Chat", command=self.new_chat).pack(pady=5)
        ctk.CTkButton(self.sidebar, text="Logout", command=self.logout).pack(pady=5, side="bottom")
        
        self.chat_list = ctk.CTkScrollableFrame(self.sidebar)
        self.chat_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_chats()
        
        # Main chat area
        self.chat_area = ctk.CTkFrame(self.main_frame)
        self.chat_area.pack(side="right", fill="both", expand=True)
        
        self.chat_display = ctk.CTkTextbox(self.chat_area, wrap="word")
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.input_frame = ctk.CTkFrame(self.chat_area)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        
        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type symptoms, query...")
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        ctk.CTkButton(self.input_frame, text="Send", command=self.send_message).pack(side="right")
        
        self.new_chat()  # Start new chat
    
    def load_chats(self):
        for widget in self.chat_list.winfo_children():
            widget.destroy()
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
            SELECT id, title, is_pinned FROM chats 
            WHERE user_id = %s ORDER BY is_pinned DESC, updated_at DESC
            """, (self.current_user['id'],))
            chats = cur.fetchall()
            cur.close()
            conn.close()
            
            for chat in chats:
                btn = ctk.CTkButton(self.chat_list, text=chat['title'] or "Chat", 
                                  command=lambda cid=chat['id']: self.load_chat(cid))
                btn.pack(fill="x", pady=2)
        except Exception as e:
            print(e)
    
    def new_chat(self):
        self.current_chat_id = None
        self.chat_history = []
        self.chat_display.delete("1.0", "end")
        self.chat_display.insert("end", "New chat started. Describe your symptoms...\n\n")
    
    def load_chat(self, chat_id):
        self.current_chat_id = chat_id
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT messages FROM chats WHERE id = %s", (chat_id,))
            data = cur.fetchone()
            cur.close()
            conn.close()
            
            self.chat_history = data['messages'] if data else []
            self.chat_display.delete("1.0", "end")
            for msg in self.chat_history:
                self.chat_display.insert("end", f"{msg['role'].upper()}: {msg['content']}\n\n")
        except Exception as e:
            print(e)
    
    def send_message(self):
        query = self.user_input.get().strip()
        if not query:
            return
        self.chat_display.insert("end", f"YOU: {query}\n\n")
        self.user_input.delete(0, "end")
        
        # Save user message
        self.chat_history.append({"role": "user", "content": query})
        
        # Get AI response in thread
        threading.Thread(target=self.process_ai_response, args=(query,), daemon=True).start()
    
    def process_ai_response(self, query):
        self.chat_display.insert("end", "HealthBot is thinking...\n")
        response = get_ai_response(query, self.chat_history)
        
        # Enhance with hospital if location mentioned (simple check)
        if "hospital" in query.lower() or "near" in query.lower():
            city = "your city"  # TODO: Prompt user or geolocation
            response += f"\n\nHospitals near you: {search_hospitals(city)}"
        
        # Update display
        self.chat_display.delete("end-2l", "end")  # Remove thinking
        self.chat_display.insert("end", f"HealthBot: {response}\n\n")
        
        self.chat_history.append({"role": "assistant", "content": response})
        
        # Save to DB
        self.save_chat()
    
    def save_chat(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            title = self.chat_history[0]['content'][:50] if self.chat_history else "Health Chat"
            
            if self.current_chat_id:
                cur.execute("""
                UPDATE chats SET messages = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
                """, (json.dumps(self.chat_history), self.current_chat_id))
            else:
                cur.execute("""
                INSERT INTO chats (user_id, title, messages)
                VALUES (%s, %s, %s) RETURNING id;
                """, (self.current_user['id'], title, json.dumps(self.chat_history)))
                self.current_chat_id = cur.fetchone()[0]
            
            conn.commit()
            cur.close()
            conn.close()
            self.load_chats()  # Refresh list
        except Exception as e:
            print("Save error:", e)
    
    def logout(self):
        self.current_user = None
        self.create_login_frame()

# ================== RUN ==================
if __name__ == "__main__":
    init_db()
    app = HealthBotApp()
    app.mainloop()

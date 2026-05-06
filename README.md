🌾 FarmersHub – Project Documentation

Developed by: Semeeha KM

📌 Project Overview

FarmersHub is a full-stack web application developed using the Django framework. The system is designed to connect farmers, sellers, customers, and delivery personnel (cargo team) within a single digital platform.

The application streamlines the process of product listing, ordering, and delivery tracking while ensuring secure, role-based access for different types of users. It aims to reduce dependency on intermediaries and improve efficiency in agricultural product distribution.

🎯 Objectives

The primary objectives of the FarmersHub system are:

To provide farmers and sellers with a platform to showcase and sell their products
To allow users to easily browse and purchase agricultural goods
To implement a structured delivery system using a dedicated cargo team
To ensure secure access through role-based authentication
To improve transparency in order tracking and delivery
⚙️ Technologies Used

Frontend:

HTML
CSS
JavaScript

Backend:

Python
Django Framework

Database:

SQLite

Other Tools:

Git & GitHub for version control
👥 System Modules
🔹 1. Admin Module

The Admin has full control over the system and is responsible for managing all operations.

Key Responsibilities:

Manage user registrations (approve/reject farmers, sellers, cargo team)
Monitor orders and bookings
Assign roles and permissions
Activate cargo team accounts (staff access)
Maintain overall system integrity
🔹 2. Farmer/Seller Module

Farmers or sellers can manage their products and view customer orders.

Features:

User registration and login
Add, update, and delete products
View order history
Track product demand
Manage inventory
🔹 3. User (Customer) Module

This module is designed for customers who purchase products.

Features:

User registration and login
Browse available products
Search and filter items
Add products to cart
Place orders
Track order status
🚚 4. Cargo Team Module (Dashboard Explanation)

The Cargo Dashboard is a restricted-access module designed specifically for delivery personnel. Unlike other users, the cargo team has limited permissions, focusing only on delivery operations.

🔐 Access Control
Cargo team members are created by the Admin
They are given staff access through the admin panel
They do NOT have full admin rights
Their dashboard is separate and role-specific
📊 Cargo Dashboard Features
1. 📦 View Assigned Orders
Cargo members can view all orders assigned for delivery
Orders include customer details, product details, and delivery address
2. 🔄 Update Delivery Status

This is the core functionality of the cargo team.

They can update order status such as:

Pending
Shipped
Out for Delivery
Delivered

👉 Important:

Cargo team can ONLY update status
They cannot modify product, user, or payment details
3. 📍 Delivery Tracking
Each status update reflects in the user’s dashboard
Ensures real-time tracking of orders
Improves transparency between users and delivery system
4. 📋 Simplified Interface
Clean and minimal dashboard UI
Focused only on delivery-related actions
Avoids unnecessary complexity
5. 🔄 Real-Time / Smooth Updates
The system can include auto-refresh or smooth reload functionality
Ensures cargo team sees updated orders without manual refresh
🧩 Key Features of the System
Role-based authentication system
Secure login and access control
Dynamic product management
Order and booking system
Dedicated cargo delivery module
Search and filtering functionality
Clean dashboard UI for all roles
Real-time status updates
🔄 System Workflow
User registers and logs into the system
User browses and selects products
User places an order
Seller receives and processes the order
Cargo team is assigned for delivery
Cargo team updates delivery status
User tracks order until successful delivery
🚀 Future Enhancements
AI-based route optimization for delivery
Chatbot support for user assistance
Online payment gateway integration
Notification system (SMS/Email alerts)
Advanced analytics dashboard
Mobile application support
📊 Project Highlights
Modular and scalable architecture
Clean and user-friendly interface
Efficient database handling using Django ORM
Secure role-based system design
Real-world applicable solution for agricultural commerce
📞 Contact

Name: Semeeha KM
Email: semeehakm72@gmail.com

Phone: 9447259734

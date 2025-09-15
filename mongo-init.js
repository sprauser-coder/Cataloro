// MongoDB initialization script
// This script creates the database and initial collections

// Switch to the cataloro database
db = db.getSiblingDB('cataloro_marketplace');

// Create collections with proper indexes
db.createCollection('users');
db.createCollection('listings');
db.createCollection('messages');
db.createCollection('notifications');
db.createCollection('transactions');
db.createCollection('tenders');
db.createCollection('menu_settings');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "user_role": 1 });

db.listings.createIndex({ "seller_id": 1 });
db.listings.createIndex({ "status": 1 });
db.listings.createIndex({ "created_at": -1 });
db.listings.createIndex({ "category": 1 });

db.messages.createIndex({ "sender_id": 1 });
db.messages.createIndex({ "recipient_id": 1 });
db.messages.createIndex({ "created_at": -1 });

db.notifications.createIndex({ "user_id": 1 });
db.notifications.createIndex({ "is_read": 1 });
db.notifications.createIndex({ "created_at": -1 });

db.transactions.createIndex({ "buyer_id": 1 });
db.transactions.createIndex({ "seller_id": 1 });
db.transactions.createIndex({ "status": 1 });

db.tenders.createIndex({ "listing_id": 1 });
db.tenders.createIndex({ "bidder_id": 1 });
db.tenders.createIndex({ "status": 1 });

print('Database and collections initialized successfully!');
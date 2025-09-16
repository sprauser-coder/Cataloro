// MongoDB initialization script
db = db.getSiblingDB('cataloro_marketplace');

// Create collections with indexes
db.createCollection('users');
db.createCollection('listings');
db.createCollection('messages');
db.createCollection('notifications');
db.createCollection('tenders');
db.createCollection('bids');
db.createCollection('transactions');
db.createCollection('system_notifications');
db.createCollection('menu_settings');
db.createCollection('ads');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });
db.users.createIndex({ "createdAt": 1 });

db.listings.createIndex({ "sellerId": 1 });
db.listings.createIndex({ "status": 1 });
db.listings.createIndex({ "category": 1 });
db.listings.createIndex({ "createdAt": -1 });
db.listings.createIndex({ "title": "text", "description": "text" });

db.messages.createIndex({ "senderId": 1 });
db.messages.createIndex({ "recipientId": 1 });
db.messages.createIndex({ "conversationId": 1 });
db.messages.createIndex({ "createdAt": -1 });

db.notifications.createIndex({ "userId": 1 });
db.notifications.createIndex({ "read": 1 });
db.notifications.createIndex({ "createdAt": -1 });

db.tenders.createIndex({ "buyerId": 1 });
db.tenders.createIndex({ "status": 1 });
db.tenders.createIndex({ "createdAt": -1 });

db.bids.createIndex({ "tenderId": 1 });
db.bids.createIndex({ "bidderId": 1 });
db.bids.createIndex({ "createdAt": -1 });

db.transactions.createIndex({ "buyerId": 1 });
db.transactions.createIndex({ "sellerId": 1 });
db.transactions.createIndex({ "status": 1 });
db.transactions.createIndex({ "createdAt": -1 });

print('Database initialization completed successfully!');
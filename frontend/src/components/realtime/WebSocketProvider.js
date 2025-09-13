import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [liveAuctions, setLiveAuctions] = useState({});
  const socketRef = useRef(null);

  useEffect(() => {
    // Get current user info from localStorage or context
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    
    if (currentUser.id) {
      initializeWebSocket(currentUser);
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  const initializeWebSocket = (user) => {
    // Temporarily disable WebSocket connection to avoid connection errors
    console.log('🔌 WebSocket connection disabled - no real-time server available');
    setIsConnected(false);
    return;
    
    // Original WebSocket connection code (disabled)
    /*
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const wsUrl = backendUrl.replace('/api', '').replace('http', 'ws');
      
      const socketInstance = io(wsUrl, {
        transports: ['websocket', 'polling'],
        auth: {
          user_id: user.id,
          username: user.username,
          user_role: user.user_role
        }
      });

      socketInstance.on('connect', () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
        setSocket(socketInstance);
        socketRef.current = socketInstance;
      });

      socketInstance.on('disconnect', () => {
        console.log('❌ WebSocket disconnected');
        setIsConnected(false);
      });

      socketInstance.on('connection_confirmed', (data) => {
        console.log('🔗 Connection confirmed:', data);
        // Request online users list
        socketInstance.emit('get_online_users', {});
      });

      socketInstance.on('online_users', (data) => {
        setOnlineUsers(data.users || []);
      });

      socketInstance.on('user_status_update', (data) => {
        if (data.status === 'online') {
          setOnlineUsers(prev => {
            const exists = prev.some(user => user.user_id === data.user_id);
            if (!exists) {
              return [...prev, {
                user_id: data.user_id,
                username: data.username,
                last_activity: data.timestamp
              }];
            }
            return prev;
          });
        } else {
          setOnlineUsers(prev => prev.filter(user => user.user_id !== data.user_id));
        }
      });

      socketInstance.on('notification', (notification) => {
        setNotifications(prev => [notification, ...prev.slice(0, 49)]); // Keep last 50
        
        // Show browser notification if permission granted
        if (Notification.permission === 'granted') {
          new Notification(notification.title || 'Cataloro Notification', {
            body: notification.message,
            icon: '/favicon.ico'
          });
        }
      });

      socketInstance.on('new_message', (message) => {
        setNotifications(prev => [{
          type: 'message',
          title: `New message from ${message.sender_username}`,
          message: message.message,
          timestamp: message.timestamp,
          data: message
        }, ...prev.slice(0, 49)]);
      });

      socketInstance.on('new_bid', (bidData) => {
        const { listing_id, bid, auction_status } = bidData;
        
        setLiveAuctions(prev => ({
          ...prev,
          [listing_id]: auction_status
        }));

        setNotifications(prev => [{
          type: 'bid',
          title: 'New Bid Placed',
          message: `€${bid.amount} bid on ${bid.listing_id}`,
          timestamp: bid.timestamp,
          data: bidData
        }, ...prev.slice(0, 49)]);
      });

      socketInstance.on('bid_received', (bidData) => {
        setNotifications(prev => [{
          type: 'bid_received',
          title: 'Bid Received on Your Listing',
          message: `${bidData.bid.bidder_username} bid €${bidData.bid.amount}`,
          timestamp: bidData.bid.timestamp,
          data: bidData
        }, ...prev.slice(0, 49)]);
      });

      socketInstance.on('auction_status', (auctionData) => {
        setLiveAuctions(prev => ({
          ...prev,
          [auctionData.listing_id]: auctionData.auction
        }));
      });

      socketInstance.on('listing_update', (updateData) => {
        // Handle real-time listing updates
        console.log('📋 Listing updated:', updateData);
      });

      socketInstance.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
      });

    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  };

  const joinRoom = (roomType, roomId) => {
    if (socket && isConnected) {
      socket.emit('join_room', { room_type: roomType, room_id: roomId });
    }
  };

  const leaveRoom = (roomType, roomId) => {
    if (socket && isConnected) {
      socket.emit('leave_room', { room_type: roomType, room_id: roomId });
    }
  };

  const sendMessage = (recipientId, message, type = 'text') => {
    if (socket && isConnected) {
      socket.emit('send_message', {
        recipient_id: recipientId,
        message: message,
        type: type
      });
    }
  };

  const placeBid = (listingId, bidAmount) => {
    if (socket && isConnected) {
      socket.emit('place_bid', {
        listing_id: listingId,
        bid_amount: bidAmount
      });
    }
  };

  const watchListing = (listingId) => {
    if (socket && isConnected) {
      socket.emit('watch_listing', { listing_id: listingId });
    }
  };

  const unwatchListing = (listingId) => {
    if (socket && isConnected) {
      socket.emit('unwatch_listing', { listing_id: listingId });
    }
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const markNotificationAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId 
          ? { ...notif, read: true }
          : notif
      )
    );
  };

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const contextValue = {
    socket,
    isConnected,
    onlineUsers,
    notifications,
    liveAuctions,
    joinRoom,
    leaveRoom,
    sendMessage,
    placeBid,
    watchListing,
    unwatchListing,
    clearNotifications,
    markNotificationAsRead
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketProvider;
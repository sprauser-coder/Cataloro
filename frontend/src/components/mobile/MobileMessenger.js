/**
 * CATALORO - Mobile Messenger Component
 * Complete mobile-optimized messaging interface
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  ArrowLeft, 
  MoreVertical, 
  Search, 
  Phone,
  Video,
  Paperclip,
  Smile,
  X,
  Check,
  CheckCheck,
  Clock,
  Info
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';

function MobileMessenger({ conversations = [], activeConversation = null, onBack }) {
  console.log('🚀 MobileMessenger component rendered - props:', { onBack: !!onBack, activeConversation });
  
  const { user } = useAuth();
  const { showToast } = useNotifications();
  
  console.log('🔐 Auth context in MobileMessenger:', { user, hasUser: !!user });
  
  const [view, setView] = useState(activeConversation ? 'conversation' : 'list'); // 'list' or 'conversation'
  const [currentConversation, setCurrentConversation] = useState(activeConversation);
  const [message, setMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [loading, setLoading] = useState(true);
  const [realConversations, setRealConversations] = useState([]);
  const [conversationMessages, setConversationMessages] = useState([]);
  const messagesEndRef = useRef(null);

  // Debug user context
  useEffect(() => {
    console.log('🔍 MobileMessenger useEffect triggered - user state:', user);
    console.log('🔍 User keys:', user ? Object.keys(user) : 'user is null/undefined');
  }, [user]);

  // Load real conversations from backend
  useEffect(() => {
    console.log('🎯 loadConversations useEffect triggered - user:', user);
    loadConversations();
  }, [user]);

  const loadConversations = async () => {
    console.log('🔄 Loading conversations - user:', user);
    if (!user) {
      console.log('❌ No user found in loadConversations');
      return;
    }
    
    try {
      setLoading(true);
      console.log('📞 Calling liveService.getUserMessages with user.id:', user.id);
      const userMessages = await liveService.getUserMessages(user.id);
      console.log('✅ Got user messages:', userMessages);
      
      // Group messages into conversations (same logic as desktop version)
      const conversationsMap = new Map();
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      
      userMessages.forEach(msg => {
        const messageDate = new Date(msg.created_at);
        
        // Skip messages older than 7 days
        if (messageDate < sevenDaysAgo) {
          return;
        }
        
        const otherUserId = msg.sender_id === user.id ? msg.recipient_id : msg.sender_id;
        const otherUserName = msg.sender_id === user.id ? msg.recipient_name : msg.sender_name;
        
        if (!conversationsMap.has(otherUserId)) {
          conversationsMap.set(otherUserId, {
            id: otherUserId,
            name: otherUserName || 'Unknown User',
            initials: (otherUserName || 'UN').substring(0, 2).toUpperCase(),
            messages: [],
            lastMessage: null,
            unreadCount: 0,
            online: Math.random() > 0.5 // Mock online status
          });
        }
        
        const conversation = conversationsMap.get(otherUserId);
        conversation.messages.push(msg);
        
        // Update last message and unread count
        if (!conversation.lastMessage || new Date(msg.created_at) > new Date(conversation.lastMessage.created_at)) {
          conversation.lastMessage = msg;
        }
        
        if (!msg.is_read && msg.sender_id !== user.id) {
          conversation.unreadCount++;
        }
      });
      
      // Convert to array and sort by last message time
      const conversationsList = Array.from(conversationsMap.values()).sort((a, b) => {
        if (!a.lastMessage && !b.lastMessage) return 0;
        if (!a.lastMessage) return 1;
        if (!b.lastMessage) return -1;
        return new Date(b.lastMessage.created_at) - new Date(a.lastMessage.created_at);
      });
      
      console.log('📋 Setting conversations list:', conversationsList);
      setRealConversations(conversationsList);
      
    } catch (error) {
      console.error('❌ Error loading conversations:', error);
      showToast('Error loading conversations', 'error');
    } finally {
      console.log('✅ Loading complete, setting loading to false');
      setLoading(false);
    }
  };

  // Mock messages for active conversation - replace with real message loading
  const [messages, setMessages] = useState([]);

  // Load conversation messages when conversation is selected
  const loadConversationMessages = async (conversation) => {
    if (conversation && conversation.messages) {
      // Convert backend message format to component format
      const formattedMessages = conversation.messages.map(msg => ({
        id: msg.id,
        text: msg.content,
        sender: msg.sender_id === user.id ? 'me' : 'them',
        timestamp: new Date(msg.created_at),
        status: msg.is_read ? 'read' : 'delivered'
      }));
      
      setMessages(formattedMessages);
    }
  };

  const handleConversationSelect = (conversation) => {
    setCurrentConversation(conversation);
    setView('conversation');
    loadConversationMessages(conversation);
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !currentConversation) {
      alert('No message or conversation selected');
      return;
    }
    
    console.log('🔄 Sending message:', message, 'to conversation:', currentConversation.id);
    
    const messageText = message;
    const tempId = Date.now();
    
    const newMessageObj = {
      id: tempId,
      text: messageText,
      sender: 'me',
      timestamp: new Date(),
      status: 'sending'
    };
    
    setMessages(prev => [...prev, newMessageObj]);
    setMessage('');
    
    try {
      console.log('📤 Calling liveService.sendMessage...');
      
      // Send message via backend with correct API format
      const response = await liveService.sendMessage({
        recipient_id: currentConversation.id,
        content: messageText,
        sender_id: user.id
      });
      
      console.log('✅ Message sent successfully:', response);
      
      // Update message status
      setMessages(prev => prev.map(msg => 
        msg.id === tempId ? { ...msg, status: 'sent' } : msg
      ));
      
      // Reload conversations to update last message
      loadConversations();
      
    } catch (error) {
      console.error('❌ Error sending message:', error);
      showToast('Failed to send message: ' + error.message, 'error');
      
      // Remove failed message
      setMessages(prev => prev.filter(msg => msg.id !== tempId));
      
      // Restore message text for user to retry
      setMessage(messageText);
    }
  };

  const scrollToBottom = () => {
    // Use scrollTop on the messages container to prevent page scrolling
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  };

  useEffect(() => {
    // Only scroll when new messages are added, with a small delay
    if (messages.length > 0) {
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 50);
      
      return () => clearTimeout(timeoutId);
    }
  }, [messages]);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatLastSeen = (date) => {
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Active now';
    if (diffInHours < 24) return `Active ${diffInHours}h ago`;
    return `Active ${Math.floor(diffInHours / 24)}d ago`;
  };

  const filteredConversations = realConversations.filter(conv =>
    conv.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderMessageStatus = (status) => {
    switch (status) {
      case 'sending':
        return <Clock className="w-3 h-3 text-gray-400" />;
      case 'sent':
        return <Check className="w-3 h-3 text-gray-400" />;
      case 'delivered':
        return <CheckCheck className="w-3 h-3 text-gray-400" />;
      case 'read':
        return <CheckCheck className="w-3 h-3 text-blue-500" />;
      default:
        return null;
    }
  };

  if (view === 'list') {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900 pb-safe-bottom">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={onBack}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
              </button>
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Messages</h1>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {realConversations.filter(c => c.unreadCount > 0).length} unread
            </div>
          </div>
          
          {/* Search Bar */}
          <div className="mt-3 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-700 border-0 rounded-lg text-sm placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600"
            />
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto pb-20">  {/* Added pb-20 for bottom spacing */}
          {loading ? (
            <div className="flex flex-col items-center justify-center h-64 text-center px-4">
              <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4 animate-pulse">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Loading conversations...</h3>
              <p className="text-gray-500 dark:text-gray-400">Please wait while we fetch your messages</p>
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center px-4">
              <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No conversations found</h3>
              <p className="text-gray-500 dark:text-gray-400">Try adjusting your search terms or start a new conversation</p>
            </div>
          ) : (
            filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => handleConversationSelect(conversation)}
                className="flex items-center space-x-3 p-4 hover:bg-gray-100 dark:hover:bg-gray-800 border-b border-gray-100 dark:border-gray-700 cursor-pointer transition-colors"
              >
                {/* Avatar */}
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium">
                      {conversation.initials}
                    </span>
                  </div>
                  {conversation.online && (
                    <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full"></div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center mb-1">
                    <h3 className="font-medium text-gray-900 dark:text-white truncate">
                      {conversation.name}
                    </h3>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {conversation.lastMessage ? formatTime(new Date(conversation.lastMessage.created_at)) : ''}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {conversation.lastMessage ? (
                      <>
                        {conversation.lastMessage.sender_id === user?.id ? 'You: ' : ''}
                        {conversation.lastMessage.content}
                      </>
                    ) : 'No messages yet'}
                  </p>
                </div>

                {/* Unread Badge */}
                {conversation.unreadCount > 0 && (
                  <div className="bg-blue-500 text-white text-xs rounded-full min-w-[20px] h-5 flex items-center justify-center px-1.5">
                    {conversation.unreadCount}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    );
  }

  // Conversation View
  return (
    <div className="flex flex-col min-h-screen bg-white dark:bg-gray-900">
      {/* Conversation Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setView('list')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-sm">
                    {currentConversation?.initials || 'UN'}
                  </span>
                </div>
                {currentConversation?.online && (
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full"></div>
                )}
              </div>
              
              <div>
                <h2 className="font-medium text-gray-900 dark:text-white">
                  {currentConversation?.name || 'Unknown User'}
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {currentConversation?.online ? 'Active now' : formatLastSeen(new Date(Date.now() - 3600000))}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <Phone className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <Video className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <MoreVertical className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-20" id="messages-container">  {/* Added pb-20 for bottom spacing */}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'me' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[75%] ${msg.sender === 'me' ? 'order-2' : 'order-1'}`}>
              <div
                className={`px-4 py-2 rounded-2xl ${
                  msg.sender === 'me'
                    ? 'bg-blue-500 text-white rounded-br-md'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
                }`}
              >
                <p className="text-sm">{msg.text}</p>
              </div>
              <div className={`flex items-center mt-1 space-x-1 ${msg.sender === 'me' ? 'justify-end' : 'justify-start'}`}>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {formatTime(msg.timestamp)}
                </span>
                {msg.sender === 'me' && renderMessageStatus(msg.status)}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input - Fixed at bottom with proper mobile spacing */}
      <div className="sticky bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4" 
           style={{ marginBottom: 'env(safe-area-inset-bottom)' }}>
        <div className="flex items-end space-x-3">
          <button className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors">
            <Paperclip className="w-5 h-5" />
          </button>
          
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type a message..."
              className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 rounded-2xl text-sm placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 resize-none"
              rows="1"
            />
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              <Smile className="w-5 h-5" />
            </button>
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!message.trim()}
            className={`p-3 rounded-full transition-colors ${
              message.trim()
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default MobileMessenger;
/**
 * CATALORO - Modern State-of-the-Art Messaging Interface
 * Full-featured messaging system with real-time capabilities
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  MessageCircle, 
  Send, 
  Search, 
  MoreHorizontal,
  User,
  Clock,
  Check,
  CheckCheck,
  Star,
  Archive,
  Trash2,
  Reply,
  X,
  Filter,
  Users,
  Mail,
  MailOpen,
  Paperclip,
  Image as ImageIcon,
  Smile,
  ArrowUp,
  Phone,
  Video,
  Settings,
  Pin,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  UserPlus,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import usePermissions from '../../hooks/usePermissions';

// Modern Message Service
class ModernMessageService {
  constructor(baseURL) {
    this.baseURL = baseURL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  async getConversations(userId) {
    const response = await fetch(`${this.baseURL}/api/messages/conversations/${userId}`);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    return response.json();
  }

  async getConversationMessages(userId, otherUserId, limit = 50, offset = 0) {
    const response = await fetch(`${this.baseURL}/api/messages/conversation/${userId}/${otherUserId}?limit=${limit}&offset=${offset}`);
    if (!response.ok) throw new Error('Failed to fetch messages');
    return response.json();
  }

  async sendMessage(messageData) {
    const response = await fetch(`${this.baseURL}/api/messages/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(messageData)
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  }

  async deleteMessage(messageId, userId) {
    const response = await fetch(`${this.baseURL}/api/messages/${messageId}?user_id=${userId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete message');
    return response.json();
  }

  async markAsRead(messageId, userId) {
    const response = await fetch(`${this.baseURL}/api/messages/${messageId}/read`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId })
    });
    if (!response.ok) throw new Error('Failed to mark as read');
    return response.json();
  }

  async searchMessages(userId, query, limit = 20) {
    const response = await fetch(`${this.baseURL}/api/messages/search/${userId}?q=${encodeURIComponent(query)}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to search messages');
    return response.json();
  }

  async searchUsers(query) {
    const response = await fetch(`${this.baseURL}/api/users/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Failed to search users');
    return response.json();
  }
}

function ModernMessagesInterface() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const { getUserDisplay } = usePermissions();
  
  // Core state
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  
  // UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [messageFilter, setMessageFilter] = useState('all');
  const [showSearch, setShowSearch] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [typingUsers, setTypingUsers] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState(new Set());
  
  // Note: Direct messaging removed - messages only through sales transactions
  
  // Refs
  const messagesEndRef = useRef(null);
  const messageInputRef = useRef(null);
  const messagesContainerRef = useRef(null);
  
  // Services
  const messageService = new ModernMessageService();
  
  // Load conversations on mount
  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

  // Auto-resize message input
  const autoResizeInput = useCallback((element) => {
    element.style.height = 'auto';
    element.style.height = Math.min(element.scrollHeight, 120) + 'px';
  }, []);

  // Scroll to bottom of messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Load conversations
  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await messageService.getConversations(user.id);
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      showToast('Failed to load conversations', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Load messages for a conversation
  const loadMessages = async (otherUserId) => {
    try {
      const data = await messageService.getConversationMessages(user.id, otherUserId);
      setMessages(data.messages || []);
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('Failed to load messages:', error);
      showToast('Failed to load messages', 'error');
    }
  };

  // Select conversation
  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    loadMessages(conversation.id);
    
    // Mark messages as read
    const unreadMessages = conversation.messages?.filter(m => 
      !m.is_read && m.sender_id !== user.id
    ) || [];
    
    unreadMessages.forEach(message => {
      messageService.markAsRead(message.id, user.id).catch(console.error);
    });
  };

  // Send message
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation || sending) return;

    const messageText = newMessage.trim();
    setNewMessage('');
    setSending(true);

    try {
      await messageService.sendMessage({
        sender_id: user.id,
        recipient_id: selectedConversation.id,
        content: messageText,
        message_type: 'text'
      });

      // Add message to UI immediately
      const tempMessage = {
        id: `temp_${Date.now()}`,
        sender_id: user.id,
        recipient_id: selectedConversation.id,
        content: messageText,
        is_read: true,
        created_at: new Date().toISOString(),
        sender: {
          id: user.id,
          username: user.username,
          full_name: user.full_name,
          badge: getUserDisplay()?.badge || 'User'
        }
      };

      setMessages(prev => [...prev, tempMessage]);
      setTimeout(scrollToBottom, 100);
      
      // Reload conversations to update last message
      setTimeout(loadConversations, 500);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      showToast('Failed to send message', 'error');
    } finally {
      setSending(false);
    }
  };

  // Handle key press in message input
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Search messages
  const searchMessages = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const data = await messageService.searchMessages(user.id, query);
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    }
  };

  // Note: Direct user search and new conversation features removed
  // Messages can only be initiated through sales transactions

  // Delete message
  const deleteMessage = async (messageId) => {
    if (!window.confirm('Delete this message?')) return;

    try {
      await messageService.deleteMessage(messageId, user.id);
      setMessages(prev => prev.filter(m => m.id !== messageId));
      showToast('Message deleted', 'success');
    } catch (error) {
      console.error('Failed to delete message:', error);
      showToast('Failed to delete message', 'error');
    }
  };

  // Filter conversations
  const filteredConversations = conversations.filter(conversation => {
    const matchesSearch = conversation.user?.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conversation.user?.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conversation.last_message?.content?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = messageFilter === 'all' || 
                         (messageFilter === 'unread' && conversation.unread_count > 0);
                         
    return matchesSearch && matchesFilter;
  });

  // Get user badge styling
  const getBadgeStyle = (badge) => {
    switch (badge) {
      case 'Admin':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'Manager':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300';
      case 'Seller':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'Buyer':
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    }
  };

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-white dark:bg-gray-900' : 'h-[calc(100vh-2rem)] mx-4 my-4'} flex flex-col rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-2xl`}>
      
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <MessageCircle className="w-8 h-8" />
            <div>
              <h1 className="text-xl font-bold">Messages</h1>
              <p className="text-blue-100 text-sm">
                {conversations.length} conversations • {conversations.reduce((sum, c) => sum + c.unread_count, 0)} unread
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSearch(!showSearch)}
              className={`p-2 rounded-lg transition-colors ${showSearch ? 'bg-white/20' : 'hover:bg-white/10'}`}
              title="Search messages"
            >
              <Search className="w-5 h-5" />
            </button>
            
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors lg:hidden"
              title="Toggle sidebar"
            >
              <Users className="w-5 h-5" />
            </button>
            
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
            >
              {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Search Bar */}
        {showSearch && (
          <div className="mt-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-blue-200" />
              <input
                type="text"
                placeholder="Search messages..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  searchMessages(e.target.value);
                }}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-200 focus:outline-none focus:bg-white/20"
              />
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex min-h-0">
        
        {/* Conversations Sidebar */}
        <div className={`${showSidebar ? 'w-80' : 'w-0'} lg:w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 ${showSidebar ? '' : 'overflow-hidden'}`}>
          
          {/* Filters & New Message */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <select
                value={messageFilter}
                onChange={(e) => setMessageFilter(e.target.value)}
                className="px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Messages</option>
                <option value="unread">Unread Only</option>
              </select>
              
              {/* New conversation button removed - conversations start through sales */}
            </div>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-6 text-center">
                <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading conversations...</p>
              </div>
            ) : filteredConversations.length === 0 ? (
              <div className="p-6 text-center">
                <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No conversations</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">Messages will appear here when you make purchases or sales</p>
              </div>
            ) : (
              filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => selectConversation(conversation)}
                  className={`p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-all duration-200 ${
                    selectedConversation?.id === conversation.id ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700' : ''
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="relative">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <User className="w-6 h-6 text-white" />
                      </div>
                      {onlineUsers.has(conversation.id) && (
                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-900"></div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2 min-w-0">
                          <p className={`text-sm font-medium ${conversation.unread_count > 0 ? 'text-gray-900 dark:text-white font-bold' : 'text-gray-700 dark:text-gray-300'} truncate`}>
                            {conversation.user?.full_name || conversation.user?.username || 'Unknown User'}
                          </p>
                          <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${getBadgeStyle(conversation.user?.badge || 'User')}`}>
                            {conversation.user?.badge || 'User'}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {conversation.unread_count > 0 && (
                            <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium animate-pulse">
                              {conversation.unread_count}
                            </span>
                          )}
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {conversation.last_message ? new Date(conversation.last_message.created_at).toLocaleDateString() : ''}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                        {conversation.last_message?.sender_id === user?.id ? 'You: ' : ''}
                        {conversation.last_message?.content || 'No messages yet'}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 flex flex-col">
          {selectedConversation ? (
            <>
              {/* Conversation Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      {onlineUsers.has(selectedConversation.id) && (
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                      )}
                    </div>
                    
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                          {selectedConversation.user?.full_name || selectedConversation.user?.username || 'Unknown User'}
                        </h3>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getBadgeStyle(selectedConversation.user?.badge || 'User')}`}>
                          {selectedConversation.user?.badge || 'User'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {onlineUsers.has(selectedConversation.id) ? 'Online' : 'Offline'} • {messages.length} messages
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                      <Phone className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                      <Video className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                      <MoreHorizontal className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div 
                ref={messagesContainerRef}
                className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50/30 to-white/50 dark:from-gray-900/30 dark:to-gray-800/50"
              >
                {messages.map((message, index) => {
                  const isOwn = message.sender_id === user?.id;
                  const showAvatar = index === 0 || messages[index - 1].sender_id !== message.sender_id;
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex ${isOwn ? 'justify-end' : 'justify-start'} ${showAvatar ? 'mt-4' : 'mt-2'}`}
                    >
                      <div className={`flex space-x-3 max-w-xs lg:max-w-md ${isOwn ? 'flex-row-reverse space-x-reverse' : ''}`}>
                        {showAvatar && (
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                            isOwn ? 'bg-blue-600' : 'bg-gray-600'
                          }`}>
                            {(isOwn ? (user?.full_name || user?.username || 'You') : message.sender?.full_name || message.sender?.username || 'U').charAt(0)}
                          </div>
                        )}
                        
                        <div className={`${!showAvatar ? (isOwn ? 'mr-11' : 'ml-11') : ''}`}>
                          <div
                            className={`group relative px-4 py-3 rounded-2xl transition-all duration-300 ${
                              isOwn
                                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                                : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                            }`}
                          >
                            {/* Delete Message Button */}
                            <button
                              onClick={() => deleteMessage(message.id)}
                              className={`absolute top-1 right-1 opacity-0 group-hover:opacity-100 p-1 rounded-full transition-all duration-200 hover:scale-110 ${
                                isOwn 
                                  ? 'bg-red-500/20 text-red-200 hover:bg-red-500/30' 
                                  : 'bg-red-500/10 text-red-600 hover:bg-red-500/20'
                              }`}
                              title="Delete message"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                            
                            <p className="text-sm whitespace-pre-wrap pr-6">{message.content}</p>
                          </div>
                          
                          <div className={`flex items-center mt-1 space-x-2 text-xs text-gray-500 dark:text-gray-400 ${isOwn ? 'justify-end' : 'justify-start'}`}>
                            <span>{new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            {isOwn && (
                              message.is_read ? 
                              <CheckCheck className="w-3 h-3 text-blue-500" /> : 
                              <Check className="w-3 h-3" />
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {/* Typing indicator */}
                {typingUsers.length > 0 && (
                  <div className="flex justify-start">
                    <div className="bg-gray-200 dark:bg-gray-700 rounded-2xl px-4 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="flex items-end space-x-4">
                  <div className="flex-1 relative">
                    <textarea
                      ref={messageInputRef}
                      value={newMessage}
                      onChange={(e) => {
                        setNewMessage(e.target.value);
                        autoResizeInput(e.target);
                      }}
                      onKeyPress={handleKeyPress}
                      placeholder="Type a message..."
                      className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                      rows="1"
                      style={{ maxHeight: '120px' }}
                      disabled={sending}
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                      <Paperclip className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                      <ImageIcon className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                      <Smile className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || sending}
                      className={`p-3 rounded-full transition-all duration-200 ${
                        newMessage.trim() && !sending
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:scale-105'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {sending ? (
                        <div className="w-5 h-5 border-2 border-white border-t-transparent animate-spin rounded-full"></div>
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* No conversation selected */
            <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900">
              <div className="text-center">
                <MessageCircle className="w-24 h-24 text-gray-300 dark:text-gray-600 mb-6" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Welcome to Messages</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">Select a conversation from the sidebar to view messages from your sales and purchases</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Note: User search modal removed - conversations only start through sales */}
    </div>
  );
}

export default ModernMessagesInterface;
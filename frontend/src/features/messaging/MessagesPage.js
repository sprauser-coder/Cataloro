/**
 * CATALORO - Comprehensive Messaging System
 * Full messaging functionality with real-time updates and enhanced UX
 * Mobile-responsive with dedicated mobile interface
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageCircle, 
  Send, 
  Search, 
  Plus, 
  MoreHorizontal,
  User,
  Clock,
  Check,
  CheckCheck,
  Star,
  Archive,
  Trash2,
  Reply,
  Forward,
  X,
  Filter,
  Users,
  Mail,
  MailOpen,
  Paperclip,
  Image as ImageIcon,
  Smile,
  Trash2 as DeleteIcon,
  Maximize2,
  Minimize2,
  ArrowUp
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';
import usePermissions from '../../hooks/usePermissions';
import MobileMessenger from '../../components/mobile/MobileMessenger';
import { useNavigate } from 'react-router-dom';

// Hook to get ads configuration
function useAdsConfig() {
  const [adsConfig, setAdsConfig] = useState(null);
  
  useEffect(() => {
    const loadAdsConfig = () => {
      try {
        const savedConfig = localStorage.getItem('cataloro_site_config');
        if (savedConfig) {
          const config = JSON.parse(savedConfig);
          setAdsConfig(config.adsManager || null);
        }
      } catch (error) {
        console.warn('Could not load ads configuration');
      }
    };

    // Load initially
    loadAdsConfig();

    // Listen for ads config updates
    const handleAdsConfigUpdate = () => {
      loadAdsConfig();
    };

    window.addEventListener('adsConfigUpdated', handleAdsConfigUpdate);
    window.addEventListener('storage', handleAdsConfigUpdate);

    return () => {
      window.removeEventListener('adsConfigUpdated', handleAdsConfigUpdate);
      window.removeEventListener('storage', handleAdsConfigUpdate);
    };
  }, []);
  
  return adsConfig;
}

function MessagesPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const { getUserDisplay } = usePermissions();
  const adsConfig = useAdsConfig();
  const navigate = useNavigate();
  
  // ALL STATE DECLARATIONS FIRST
  const [isMobile, setIsMobile] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const [newMessage, setNewMessage] = useState({ recipient: '', subject: '', content: '' });
  const [replyMessage, setReplyMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCompose, setShowCompose] = useState(false);
  const [messageFilter, setMessageFilter] = useState('all'); // all, unread, sent
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNewMessagePopup, setShowNewMessagePopup] = useState(false);
  const [newMessagePopup, setNewMessagePopup] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [sending, setSending] = useState(false);
  const [isFullPageChat, setIsFullPageChat] = useState(false);
  const [highlightedMessageId, setHighlightedMessageId] = useState(null);
  const [sessionReadMessages, setSessionReadMessages] = useState(new Set());
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [userSearchResults, setUserSearchResults] = useState([]);
  const [showUserSearch, setShowUserSearch] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // ALL REFS
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const messageRefs = useRef({});

  // ALL EFFECTS BEFORE CONDITIONAL RETURN
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    return () => {
      console.log('🔄 Leaving Messages area - resetting read status');
      // Reset all session read messages back to unread status
      // For now, we'll just clear the local session state
      
      // Trigger header notification update to restore original counts
      window.dispatchEvent(new CustomEvent('messagesSessionReset'));
    };
  }, []); // Empty dependency array to prevent infinite loop

  // Load messages when user is available
  useEffect(() => {
    if (user && !isMobile) {
      console.log('🔄 Loading messages for desktop version...');
      loadMessages();
    }
  }, [user, isMobile]);

  // Auto-scroll effect - MOVED BEFORE CONDITIONAL RETURN TO FIX HOOKS VIOLATION
  useEffect(() => {
    // Auto-scroll to bottom when messages change (for desktop consistency with mobile)
    if (conversationMessages.length > 0 && !isMobile) {
      setTimeout(() => {
        scrollToBottom();
      }, 100);
    }
  }, [conversationMessages, isMobile]);

  // CONDITIONAL RETURN AFTER ALL HOOKS
  if (isMobile) {
    return (
      <div className="fixed inset-0 z-50 bg-gray-50 dark:bg-gray-900">
        <MobileMessenger onBack={() => navigate('/browse')} />
      </div>
    );
  }

  // Helper function to get user badge info (mocked for demo)
  const getUserBadgeInfo = (userId, userName) => {
    // In a real app, this would fetch from user data
    // For demo purposes, we'll determine based on patterns in the name or use current user data
    if (userId === user?.id) {
      const currentUserDisplay = getUserDisplay();
      return {
        badge: currentUserDisplay?.badge || 'Buyer',
        role: currentUserDisplay?.role || 'User-Buyer'
      };
    }
    
    // Mock badge assignment based on name patterns for demo
    if (userName?.toLowerCase().includes('seller') || userName?.toLowerCase().includes('john')) {
      return { badge: 'Seller', role: 'User-Seller' };
    } else if (userName?.toLowerCase().includes('admin')) {
      return { badge: 'Admin', role: 'Admin' };
    } else {
      return { badge: 'Buyer', role: 'User-Buyer' };
    }
  };

  // Helper function to get badge styling
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

  // Enhanced scroll to message function
  const scrollToMessage = (messageId) => {
    const messageElement = messageRefs.current[messageId];
    if (messageElement) {
      messageElement.scrollIntoView({ 
        behavior: "smooth", 
        block: "center" 
      });
      
      // Highlight the message
      setHighlightedMessageId(messageId);
      
      // Remove highlight after 3 seconds
      setTimeout(() => {
        setHighlightedMessageId(null);
      }, 3000);
    }
  };

  // Toggle full page chat
  const toggleFullPageChat = () => {
    setIsFullPageChat(!isFullPageChat);
  };

  // Scroll to bottom of messages container only (not the entire page)
  const scrollToBottom = () => {
    const messagesContainer = document.getElementById('desktop-messages-container');
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  };

  // Auto-scroll useEffect moved above conditional return to fix hooks violation

  // Auto-resize textarea
  const autoResizeTextarea = (element) => {
    element.style.height = 'auto';
    element.style.height = Math.min(element.scrollHeight, 120) + 'px';
  };

  // User search functionality
  const handleUserSearch = async (query) => {
    setUserSearchQuery(query);
    
    if (query.trim().length < 2) {
      setUserSearchResults([]);
      setShowUserSearch(false);
      return;
    }

    try {
      const results = await liveService.searchUsers(query);
      setUserSearchResults(results);
      setShowUserSearch(results.length > 0);
    } catch (error) {
      console.error('Error searching users:', error);
      setUserSearchResults([]);
      setShowUserSearch(false);
    }
  };

  const selectUser = (selectedUserData) => {
    setSelectedUser(selectedUserData);
    setNewMessage(prev => ({ ...prev, recipient: selectedUserData.id }));
    setUserSearchQuery(selectedUserData.display_name || selectedUserData.username);
    setShowUserSearch(false);
  };

  // Handle deleting a conversation
  const handleDeleteConversation = async (conversationId) => {
    if (!window.confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      return;
    }
    
    try {
      // TODO: Add API call to delete conversation
      // await liveService.deleteConversation(conversationId);
      
      // Remove from local state
      setConversations(conversations.filter(c => c.conversation_id !== conversationId));
      if (selectedConversation?.conversation_id === conversationId) {
        setSelectedConversation(null);
        setConversationMessages([]);
      }
      
      showToast('Conversation deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      showToast('Failed to delete conversation', 'error');
    }
  };

  // Handle deleting a single message
  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('Are you sure you want to delete this message?')) {
      return;
    }
    
    try {
      // TODO: Add API call to delete message
      // await liveService.deleteMessage(messageId);
      
      // Remove from local state
      setConversationMessages(conversationMessages.filter(m => m.id !== messageId));
      
      showToast('Message deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete message:', error);
      showToast('Failed to delete message', 'error');
    }
  };

  const loadMessages = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const userMessages = await liveService.getUserMessages(user.id);
      
      // Group messages into conversations
      const conversationsMap = new Map();
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
      
      userMessages.forEach(msg => {
        const messageDate = new Date(msg.created_at);
        
        // Skip messages older than 7 days (auto-delete feature)
        if (messageDate < sevenDaysAgo) {
          return;
        }
        
        const otherUserId = msg.sender_id === user.id ? msg.recipient_id : msg.sender_id;
        const otherUserName = msg.sender_id === user.id ? msg.recipient_name : msg.sender_name;
        
        if (!conversationsMap.has(otherUserId)) {
          conversationsMap.set(otherUserId, {
            id: otherUserId,
            name: otherUserName || 'Unknown User',
            messages: [],
            lastMessage: null,
            unreadCount: 0
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
      
      // Show notification if chats were auto-deleted
      if (userMessages.length > conversationsList.reduce((total, conv) => total + conv.messages.length, 0)) {
        showToast('⚠️ Some conversations older than 7 days have been automatically removed', 'info');
      }
      
      setConversations(conversationsList);
    } catch (error) {
      console.error('Failed to load messages:', error);
      showToast('Failed to load messages', 'error');
      // Demo data fallback
      setConversations(demoConversations);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = (conversation) => {
    console.log('🎯 selectConversation called for:', conversation.name);
    
    setSelectedConversation(conversation);
    // Sort messages chronologically (oldest first, newest at bottom) - consistent with mobile
    const sortedMessages = conversation.messages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    setConversationMessages(sortedMessages);
    
    // Immediately update conversation display to remove red badge
    setConversations(prev => 
      prev.map(conv => 
        conv.id === conversation.id 
          ? { ...conv, unreadCount: 0 }
          : conv
      )
    );
    
    // Update header immediately by reducing unread count
    const previousUnreadCount = conversation.unreadCount || 0;
    if (previousUnreadCount > 0) {
      console.log(`📧 Immediately updating header - reducing count by ${previousUnreadCount}`);
      
      // Dispatch event to update header
      window.dispatchEvent(new CustomEvent('messagesMarkedAsRead', {
        detail: { 
          count: previousUnreadCount
        }
      }));
      
      // Mark messages as read on server (async, in background)
      const unreadMessages = conversation.messages.filter(msg => !msg.is_read && msg.sender_id !== user.id);
      unreadMessages.forEach(msg => {
        console.log(`📝 Marking message ${msg.id} as read on server`);
        handleMarkAsRead(msg.id);
      });
    }
  };

  const handleSendMessage = async () => {
    if (!selectedUser || !newMessage.content.trim()) {
      showToast('Please select a recipient and enter message content', 'error');
      return;
    }

    try {
      setSending(true);
      await liveService.sendMessage(user.id, {
        recipient_id: selectedUser.id,
        subject: newMessage.subject || 'New Message',
        content: newMessage.content
      });
      
      showToast('Message sent successfully!', 'success');
      setNewMessage({ recipient: '', subject: '', content: '' });
      setSelectedUser(null);
      setUserSearchQuery('');
      setShowCompose(false);
      await loadMessages();
    } catch (error) {
      console.error('Failed to send message:', error);
      showToast('Failed to send message', 'error');
    } finally {
      setSending(false);
    }
  };

  const handleSendReply = async () => {
    if (!replyMessage.trim() || !selectedConversation) return;

    const messageToSend = replyMessage; // Store the message content before clearing

    try {
      setSending(true);
      await liveService.sendMessage(user.id, {
        recipient_id: selectedConversation.id,
        subject: `Re: ${conversationMessages[0]?.subject || 'Conversation'}`,
        content: messageToSend
      });
      
      setReplyMessage('');
      
      // Add the new message to the top of the current conversation immediately
      const newMessage = {
        id: `temp_${Date.now()}`,
        sender_id: user.id,
        sender_name: user?.full_name || user?.username || 'You',
        recipient_id: selectedConversation.id,
        subject: `Re: ${conversationMessages[0]?.subject || 'Conversation'}`,
        content: messageToSend,
        is_read: true,
        created_at: new Date().toISOString()
      };
      
      // Add new message to the end (bottom) of the conversation for chronological order
      setConversationMessages(prev => [...prev, newMessage]);
      
      // Reload messages in background to sync with server
      setTimeout(() => loadMessages(), 1000);
    } catch (error) {
      console.error('Failed to send reply:', error);
      showToast('Failed to send reply', 'error');
    } finally {
      setSending(false);
    }
  };

  const handleMarkAsRead = async (messageId) => {
    if (!user) return;
    
    try {
      await liveService.markMessageRead(user.id, messageId);
      
      // Update local state
      setConversationMessages(prev => 
        prev.map(msg => msg.id === messageId ? { ...msg, is_read: true } : msg)
      );
      
      setConversations(prev => 
        prev.map(conv => ({
          ...conv,
          messages: conv.messages.map(msg => 
            msg.id === messageId ? { ...msg, is_read: true } : msg
          ),
          unreadCount: Math.max(0, conv.unreadCount - 1)
        }))
      );
    } catch (error) {
      console.error('Failed to mark message as read:', error);
    }
  };

  const filteredConversations = conversations.filter(conversation => {
    const matchesSearch = conversation.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conversation.lastMessage?.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conversation.lastMessage?.content?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = messageFilter === 'all' || 
                         (messageFilter === 'unread' && conversation.unreadCount > 0) ||
                         (messageFilter === 'sent' && conversation.lastMessage?.sender_id === user?.id);
                         
    return matchesSearch && matchesFilter;
  });

  // Demo data for when backend is not available
  const demoConversations = [
    {
      id: 'user1',
      conversation_id: 'conv1',
      name: 'John Seller',
      participants: [
        { id: 'user1', name: 'John Seller' },
        { id: user?.id || 'demo_user', name: user?.full_name || 'Demo User' }
      ],
      messages: [
        {
          id: '1',
          sender_id: 'user1',
          sender_name: 'John Seller',
          recipient_id: user?.id || 'demo_user',
          subject: 'Question about your MacBook Pro listing',
          content: 'Hi! Is the MacBook Pro still available? I\'m very interested and can pick it up today. I can offer the full asking price.',
          is_read: false,
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        },
        {
          id: '4',
          sender_id: user?.id || 'demo_user',
          sender_name: user?.full_name || 'Demo User',
          recipient_id: 'user1',
          subject: 'Re: Question about your MacBook Pro listing',
          content: 'Yes, it\'s still available! When would be a good time for you to pick it up?',
          is_read: true,
          created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
        },
        {
          id: '5',
          sender_id: 'user1',
          sender_name: 'John Seller',
          recipient_id: user?.id || 'demo_user',
          subject: 'Re: Question about your MacBook Pro listing',
          content: 'Great! When would be a good time to meet?',
          is_read: true,
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
        }
      ],
      lastMessage: null,
      unreadCount: 0
    },
    {
      id: 'user2',
      conversation_id: 'conv2',
      name: 'Sarah Buyer',
      participants: [
        { id: 'user2', name: 'Sarah Buyer' },
        { id: user?.id || 'demo_user', name: user?.full_name || 'Demo User' }
      ],
      messages: [
        {
          id: '2',
          sender_id: 'user2',
          sender_name: 'Sarah Buyer',
          recipient_id: user?.id,
          subject: 'Purchase inquiry',
          content: 'Hello, I saw your vintage guitar listing. Would you consider $800? I\'m a serious buyer and can meet today.',
          is_read: false,
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
        }
      ],
      lastMessage: null,
      unreadCount: 1
    }
  ];

  // Calculate demo lastMessage and initialize
  demoConversations.forEach(conv => {
    conv.lastMessage = conv.messages[conv.messages.length - 1];
    conv.unreadCount = conv.messages.filter(msg => !msg.is_read && msg.sender_id !== user?.id).length;
  });

  return (
    <div className={`${isFullPageChat ? 'fixed inset-0 z-50 bg-white dark:bg-gray-900' : 'min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900'}`}>
      <div className={`${isFullPageChat ? 'h-full' : 'max-w-6xl mx-auto min-h-[calc(100vh-8rem)] max-h-[calc(100vh-8rem)]'} flex flex-col ${isFullPageChat ? 'p-0' : 'm-4'}`}>
        
        {/* Enhanced Header - No Background */}
        <div className="border-b border-white/20 p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
                <MessageCircle className="w-8 h-8 mr-3 text-blue-600" />
                Messages
                {conversations.reduce((total, conv) => total + conv.unreadCount, 0) > 0 && (
                  <span className="ml-3 bg-red-500 text-white text-sm px-3 py-1 rounded-full">
                    {conversations.reduce((total, conv) => total + conv.unreadCount, 0)} unread
                  </span>
                )}
              </h1>
              <p className="text-gray-600 dark:text-gray-300">Communicate with buyers and sellers</p>
            </div>
            <div className="flex items-center space-x-4 mt-4 lg:mt-0">
              {/* Full Page Chat Toggle Button */}
              <button
                onClick={toggleFullPageChat}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl font-medium transition-all duration-200 flex items-center shadow-lg hover:shadow-xl transform hover:scale-105"
                title={isFullPageChat ? "Exit full page" : "Enter full page chat"}
              >
                {isFullPageChat ? (
                  <>
                    <Minimize2 className="w-5 h-5 mr-2" />
                    Exit Full Page
                  </>
                ) : (
                  <>
                    <Maximize2 className="w-5 h-5 mr-2" />
                    Full Page Chat
                  </>
                )}
              </button>
              
              {/* Message Filter */}
              <select
                value={messageFilter}
                onChange={(e) => setMessageFilter(e.target.value)}
                className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Messages</option>
                <option value="unread">Unread</option>
                <option value="sent">Sent</option>
              </select>
              
              {/* New Message button removed - only buyer and seller connections allowed */}
            </div>
          </div>
        </div>

        {/* Main Layout - No Visible Containers */}
        <div className="flex flex-1 min-h-0">
          {/* Conversations List */}
          <div className={`${adsConfig?.messengerAd?.active ? 'w-1/4' : 'w-1/3'} border-r border-gray-200/30 dark:border-gray-700/30`}>
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-3 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="overflow-y-auto flex-1">
              {loading ? (
                <div className="p-6 text-center">
                  <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
                  <p className="text-gray-600 dark:text-gray-400">Loading conversations...</p>
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="p-6 text-center">
                  <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No conversations</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">Start a conversation with buyers and sellers</p>
                  {/* Start new conversation button removed - only buyer-seller connections */}
                </div>
              ) : (
                filteredConversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    onClick={() => selectConversation(conversation)}
                    className={`p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-all duration-200 ${
                      selectedConversation?.id === conversation.id ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <User className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center space-x-2 min-w-0">
                            <p className={`text-sm font-medium ${conversation.unreadCount > 0 ? 'text-gray-900 dark:text-white font-bold' : 'text-gray-700 dark:text-gray-300'} truncate`}>
                              {conversation.name}
                            </p>
                            {/* User Badge */}
                            {(() => {
                              const otherUserId = conversation.messages?.[0]?.sender_id === user?.id 
                                ? conversation.messages?.[0]?.recipient_id 
                                : conversation.messages?.[0]?.sender_id;
                              const badgeInfo = getUserBadgeInfo(otherUserId, conversation.name);
                              return (
                                <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${getBadgeStyle(badgeInfo.badge)}`}>
                                  {badgeInfo.badge}
                                </span>
                              );
                            })()}
                          </div>
                          <div className="flex items-center space-x-2">
                            {conversation.unreadCount > 0 && (
                              <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium animate-pulse">
                                {conversation.unreadCount}
                              </span>
                            )}
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {conversation.lastMessage ? new Date(conversation.lastMessage.created_at).toLocaleDateString() : ''}
                            </span>
                          </div>
                        </div>
                        <p 
                          className="text-sm text-gray-600 dark:text-gray-400 truncate mb-1 cursor-pointer hover:text-blue-600 dark:hover:text-blue-400"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (conversation.lastMessage) {
                              selectConversation(conversation);
                              setTimeout(() => scrollToMessage(conversation.lastMessage.id), 100);
                            }
                          }}
                          title="Click to scroll to this message"
                        >
                          {conversation.lastMessage?.subject || 'No subject'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 truncate">
                          {conversation.lastMessage?.sender_id === user?.id ? 'You: ' : ''}
                          {conversation.lastMessage?.content || 'No messages yet'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Message Thread - No Background */}
          <div className="flex-1 flex flex-col">
            {selectedConversation ? (
              <>
                {/* Thread Header - Simplified, No Background */}
                <div className="p-4 border-b border-gray-200/30 dark:border-gray-700/30 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                            {selectedConversation.name}
                          </h3>
                          {/* User Badge in Thread Header */}
                          {(() => {
                            const otherUserId = selectedConversation.participants?.find(p => p.id !== user?.id)?.id;
                            const badgeInfo = getUserBadgeInfo(otherUserId, selectedConversation.name);
                            return (
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getBadgeStyle(badgeInfo.badge)}`}>
                                {badgeInfo.badge}
                              </span>
                            );
                          })()}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {conversationMessages.length} messages
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {/* Delete Conversation Button */}
                      <button 
                        onClick={() => handleDeleteConversation(selectedConversation.conversation_id)}
                        className="p-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                        title="Delete conversation"
                      >
                        <DeleteIcon className="w-5 h-5" />
                      </button>
                      {/* View User Profile Button */}
                      <button 
                        onClick={() => {
                          const otherUserId = selectedConversation.participants?.find(p => p.id !== user?.id)?.id || 'unknown';
                          window.location.href = `/profile/${otherUserId}`;
                        }}
                        className="p-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                        title="View user profile"
                      >
                        <User className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Messages - Clean design without headers */}
                <div id="desktop-messages-container" className="flex-1 overflow-y-auto p-6 space-y-3 bg-gradient-to-b from-gray-50/30 to-white/50 dark:from-gray-900/30 dark:to-gray-800/50">
                  {/* Messages - chronological order (oldest first, newest at bottom) */}
                  {conversationMessages
                    .slice() // Create a copy to avoid mutating original array
                    .map((message, index, messageArray) => {
                    const isOwn = message.sender_id === user?.id;
                    const showAvatar = index === 0 || messageArray[index - 1].sender_id !== message.sender_id;
                    const isHighlighted = highlightedMessageId === message.id;
                    
                    return (
                      <div
                        key={message.id}
                        ref={(el) => messageRefs.current[message.id] = el}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'} ${showAvatar ? 'mt-4' : 'mt-2'} ${
                          isHighlighted ? 'animate-pulse' : ''
                        }`}
                      >
                        <div className={`flex space-x-3 max-w-xs lg:max-w-md ${isOwn ? 'flex-row-reverse space-x-reverse' : ''}`}>
                          {showAvatar && (
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                              isOwn ? 'bg-blue-600' : 'bg-gray-600'
                            }`}>
                              {(isOwn ? (user?.full_name || user?.username || 'You') : message.sender_name || 'U').charAt(0)}
                            </div>
                          )}
                          <div className={`${!showAvatar ? (isOwn ? 'mr-11' : 'ml-11') : ''}`}>
                            <div
                              className={`group relative px-4 py-3 rounded-2xl transition-all duration-300 ${
                                isHighlighted 
                                  ? 'ring-2 ring-yellow-400 bg-yellow-50 dark:bg-yellow-900/20' 
                                  : isOwn
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                              }`}
                            >
                              {/* Delete Message Button */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteMessage(message.id);
                                }}
                                className={`absolute top-1 right-1 opacity-0 group-hover:opacity-100 p-1 rounded-full transition-all duration-200 hover:scale-110 ${
                                  isOwn 
                                    ? 'bg-red-500/20 text-red-200 hover:bg-red-500/30' 
                                    : 'bg-red-500/10 text-red-600 hover:bg-red-500/20'
                                }`}
                                title="Delete message"
                              >
                                <DeleteIcon className="w-3 h-3" />
                              </button>
                              
                              {/* Message content without subject headers */}
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
                  
                  {/* Scroll target for new messages */}
                  <div ref={messagesEndRef} />
                </div>

                {/* Reply Box */}
                <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl">
                  <div className="flex items-end space-x-4">
                    <div className="flex-1 relative">
                      <textarea
                        ref={textareaRef}
                        value={replyMessage}
                        onChange={(e) => {
                          setReplyMessage(e.target.value);
                          autoResizeTextarea(e.target);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSendReply();
                          }
                        }}
                        placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                        className="w-full px-4 py-3 pr-12 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 resize-none min-h-[3rem] max-h-[8rem]"
                        rows="1"
                      />
                      <button className="absolute right-3 bottom-3 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                        <Smile className="w-5 h-5" />
                      </button>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="p-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                        <Paperclip className="w-5 h-5" />
                      </button>
                      <button
                        onClick={handleSendReply}
                        disabled={!replyMessage.trim() || sending}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-3 rounded-xl transition-all duration-200 transform hover:scale-105 disabled:scale-100"
                      >
                        {sending ? (
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <Send className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
                <div className="text-center">
                  <MessageCircle className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Select a conversation</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">Choose a conversation from the list to start messaging</p>
                  {/* Start new conversation button removed - only buyer-seller connections */}
                </div>
              </div>
            )}
          </div>

          {/* Messenger Advertisement */}
          {adsConfig?.messengerAd?.active && adsConfig.messengerAd.image && (
            <div 
              className="border-l border-gray-200/30 dark:border-gray-700/30 p-4"
              style={{ 
                width: adsConfig.messengerAd.width || '250px',
                minWidth: adsConfig.messengerAd.width || '250px'
              }}
            >
              <div 
                className={`bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow h-fit ${adsConfig.messengerAd.url ? 'cursor-pointer' : ''}`}
                onClick={() => {
                  if (adsConfig.messengerAd.url) {
                    // Track ad click using utility function
                    try {
                      // Import the tracking function dynamically
                      import('../../utils/adsConfiguration').then(({ trackAdClick }) => {
                        trackAdClick('messengerAd');
                      });
                    } catch (error) {
                      console.warn('Could not track ad click:', error);
                    }
                    console.log('Messenger ad clicked:', adsConfig.messengerAd.url);
                    window.open(adsConfig.messengerAd.url, '_blank');
                  }
                }}
              >
                <img
                  src={adsConfig.messengerAd.image}
                  alt={adsConfig.messengerAd.description || 'Advertisement'}
                  className="w-full object-cover"
                  style={{ height: adsConfig.messengerAd.height || '400px' }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Compose modal removed - only buyer-seller connections allowed */}
      </div>

      {/* New Message Popup */}
      {showNewMessagePopup && newMessagePopup && (
        <div className="fixed top-4 right-4 z-[10000] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl p-4 max-w-sm animate-slide-in-right">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <MessageCircle className="w-4 h-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  New message from {newMessagePopup.sender}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {newMessagePopup.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowNewMessagePopup(false)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
            {newMessagePopup.content}
          </p>
          <div className="flex space-x-2">
            <button
              onClick={() => {
                setShowNewMessagePopup(false);
                // Focus on the conversation if it's open
                const conversation = conversations.find(c => c.name === newMessagePopup.sender);
                if (conversation) {
                  selectConversation(conversation);
                }
              }}
              className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-xs hover:bg-blue-700 transition-colors"
            >
              Reply
            </button>
            <button
              onClick={() => setShowNewMessagePopup(false)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md text-xs hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default MessagesPage;
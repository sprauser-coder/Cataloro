/**
 * CATALORO - Comprehensive Messaging System
 * Full messaging functionality with real-time updates and enhanced UX
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
  Phone,
  Video,
  Info
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';

function MessagesPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  
  const [messages, setMessages] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const [newMessage, setNewMessage] = useState({ recipient: '', subject: '', content: '' });
  const [replyMessage, setReplyMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCompose, setShowCompose] = useState(false);
  const [messageFilter, setMessageFilter] = useState('all'); // all, unread, sent
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversationMessages]);

  useEffect(() => {
    if (user) {
      loadMessages();
    }
  }, [user]);

  // Auto-resize textarea
  const autoResizeTextarea = (element) => {
    element.style.height = 'auto';
    element.style.height = Math.min(element.scrollHeight, 120) + 'px';
  };

  const loadMessages = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const userMessages = await liveService.getUserMessages(user.id);
      
      // Group messages into conversations
      const conversationsMap = new Map();
      userMessages.forEach(msg => {
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
      const conversations = Array.from(conversationsMap.values()).sort((a, b) => {
        if (!a.lastMessage && !b.lastMessage) return 0;
        if (!a.lastMessage) return 1;
        if (!b.lastMessage) return -1;
        return new Date(b.lastMessage.created_at) - new Date(a.lastMessage.created_at);
      });
      
      setMessages(conversations);
    } catch (error) {
      console.error('Failed to load messages:', error);
      showToast('Failed to load messages', 'error');
      // Demo data fallback
      setMessages(demoConversations);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    setConversationMessages(conversation.messages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)));
    
    // Mark messages as read
    conversation.messages
      .filter(msg => !msg.is_read && msg.sender_id !== user.id)
      .forEach(msg => handleMarkAsRead(msg.id));
  };

  const handleSendMessage = async () => {
    if (!newMessage.recipient || !newMessage.content) {
      showToast('Please fill in recipient and message content', 'error');
      return;
    }

    try {
      setSending(true);
      await liveService.sendMessage(user.id, {
        recipient_id: newMessage.recipient,
        subject: newMessage.subject,
        content: newMessage.content
      });
      
      showToast('Message sent successfully!', 'success');
      setNewMessage({ recipient: '', subject: '', content: '' });
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

    try {
      setSending(true);
      await liveService.sendMessage(user.id, {
        recipient_id: selectedConversation.id,
        subject: `Re: ${conversationMessages[0]?.subject || 'Conversation'}`,
        content: replyMessage
      });
      
      setReplyMessage('');
      await loadMessages();
      
      // Refresh the conversation
      const updatedConversation = messages.find(c => c.id === selectedConversation.id);
      if (updatedConversation) {
        selectConversation(updatedConversation);
      }
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
      
      setMessages(prev => 
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

  const filteredMessages = messages.filter(conversation => {
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
      name: 'John Seller',
      messages: [
        {
          id: '1',
          sender_id: 'user1',
          sender_name: 'John Seller',
          recipient_id: user?.id,
          subject: 'Question about your MacBook Pro listing',
          content: 'Hi! Is the MacBook Pro still available? I\'m very interested and can pick it up today.',
          is_read: false,
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        }
      ],
      lastMessage: null,
      unreadCount: 1
    },
    {
      id: 'user2', 
      name: 'Sarah Buyer',
      messages: [
        {
          id: '2',
          sender_id: 'user2',
          sender_name: 'Sarah Buyer',
          recipient_id: user?.id,
          subject: 'Purchase inquiry',
          content: 'Hello, I saw your vintage guitar listing. Would you consider $800? I\'m a serious buyer.',
          is_read: true,
          created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
        }
      ],
      lastMessage: null,
      unreadCount: 0
    }
  ];

  // Calculate demo lastMessage and initialize
  demoConversations.forEach(conv => {
    conv.lastMessage = conv.messages[conv.messages.length - 1];
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
                <MessageCircle className="w-8 h-8 mr-3 text-blue-600" />
                Messages
              </h1>
              <p className="text-gray-600 dark:text-gray-300">Communicate with buyers and sellers</p>
            </div>
            <button
              onClick={() => setShowCompose(true)}
              className="cataloro-button-primary mt-4 lg:mt-0 flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Message
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Messages List */}
          <div className="lg:col-span-1">
            <div className="cataloro-card-glass h-full">
              <div className="p-6 border-b border-white/10 dark:border-white/10">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search messages..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 cataloro-input w-full"
                  />
                </div>
              </div>
              
              <div className="overflow-y-auto max-h-96">
                {loading ? (
                  <div className="p-6 text-center">
                    <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
                    <p className="text-gray-600 dark:text-gray-400">Loading messages...</p>
                  </div>
                ) : filteredMessages.length === 0 ? (
                  <div className="p-6 text-center">
                    <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No messages</h3>
                    <p className="text-gray-600 dark:text-gray-400">Start a conversation with buyers and sellers</p>
                  </div>
                ) : (
                  filteredMessages.map((message) => (
                    <div
                      key={message.id}
                      onClick={() => setSelectedMessage(message)}
                      className={`p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                        selectedMessage?.id === message.id ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <User className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <p className={`text-sm font-medium ${!message.is_read ? 'text-gray-900 dark:text-white font-bold' : 'text-gray-700 dark:text-gray-300'}`}>
                              {message.sender_id === user?.id ? `To: ${message.recipient_name || 'Unknown'}` : message.sender_name || 'Unknown Sender'}
                            </p>
                            {!message.is_read && message.sender_id !== user?.id && (
                              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 truncate mb-1">
                            {message.subject || 'No subject'}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            {new Date(message.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Message Detail */}
          <div className="lg:col-span-2">
            <div className="cataloro-card-glass h-full">
              {selectedMessage ? (
                <div className="flex flex-col h-full">
                  {/* Message Header */}
                  <div className="p-6 border-b border-white/10 dark:border-white/10">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                          {selectedMessage.subject || 'No subject'}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          From: {selectedMessage.sender_id === user?.id ? 'You' : selectedMessage.sender_name || 'Unknown'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {new Date(selectedMessage.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {!selectedMessage.is_read && selectedMessage.sender_id !== user?.id && (
                          <button
                            onClick={() => handleMarkAsRead(selectedMessage.id)}
                            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                            title="Mark as read"
                          >
                            <Check className="w-5 h-5" />
                          </button>
                        )}
                        <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                          <MoreHorizontal className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Message Content */}
                  <div className="flex-1 p-6">
                    <div className="prose dark:prose-invert max-w-none">
                      <p className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                        {selectedMessage.content}
                      </p>
                    </div>
                  </div>

                  {/* Reply Section */}
                  <div className="p-6 border-t border-white/10 dark:border-white/10">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => {
                          setNewMessage({
                            recipient: selectedMessage.sender_id === user?.id ? selectedMessage.recipient_id : selectedMessage.sender_id,
                            subject: `Re: ${selectedMessage.subject || 'No subject'}`,
                            content: ''
                          });
                          setShowCompose(true);
                        }}
                        className="cataloro-button-primary flex items-center"
                      >
                        <Reply className="w-4 h-4 mr-2" />
                        Reply
                      </button>
                      <button className="cataloro-button-secondary flex items-center">
                        <Forward className="w-4 h-4 mr-2" />
                        Forward
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full p-12">
                  <div className="text-center">
                    <MessageCircle className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Select a message</h3>
                    <p className="text-gray-600 dark:text-gray-400">Choose a conversation from the list to view details</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Compose Modal */}
        {showCompose && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="cataloro-card-glass max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="p-6 border-b border-white/10 dark:border-white/10">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">New Message</h3>
                  <button
                    onClick={() => setShowCompose(false)}
                    className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Recipient (User ID)
                  </label>
                  <input
                    type="text"
                    value={newMessage.recipient}
                    onChange={(e) => setNewMessage({ ...newMessage, recipient: e.target.value })}
                    className="cataloro-input w-full"
                    placeholder="Enter recipient user ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={newMessage.subject}
                    onChange={(e) => setNewMessage({ ...newMessage, subject: e.target.value })}
                    className="cataloro-input w-full"
                    placeholder="Enter message subject"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Message
                  </label>
                  <textarea
                    value={newMessage.content}
                    onChange={(e) => setNewMessage({ ...newMessage, content: e.target.value })}
                    rows={6}
                    className="cataloro-input w-full resize-none"
                    placeholder="Type your message here..."
                  />
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    onClick={() => setShowCompose(false)}
                    className="cataloro-button-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSendMessage}
                    className="cataloro-button-primary flex items-center"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Send Message
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MessagesPage;
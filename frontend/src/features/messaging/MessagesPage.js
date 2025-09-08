/**
 * CATALORO - Messages Page with Modern Interface
 * Updated to use the new state-of-the-art messaging system
 */

import React from 'react';
import ModernMessagesInterface from '../../components/messaging/ModernMessagesInterface';

function MessagesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <ModernMessagesInterface />
    </div>
  );
}

export default MessagesPage;
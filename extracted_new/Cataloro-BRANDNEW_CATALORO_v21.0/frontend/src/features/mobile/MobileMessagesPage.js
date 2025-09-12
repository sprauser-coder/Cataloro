/**
 * CATALORO - Mobile Messages Page
 * Full-screen mobile messaging experience
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import MobileMessenger from '../../components/mobile/MobileMessenger';

function MobileMessagesPage() {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/browse');
  };

  return (
    <div className="lg:hidden">
      <MobileMessenger onBack={handleBack} />
    </div>
  );
}

export default MobileMessagesPage;
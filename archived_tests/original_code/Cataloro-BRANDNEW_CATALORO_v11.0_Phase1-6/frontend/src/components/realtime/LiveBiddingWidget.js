import React, { useState, useEffect } from 'react';
import { useWebSocket } from './WebSocketProvider';

const LiveBiddingWidget = ({ listing, currentUser, onBidPlaced }) => {
  const { isConnected, liveAuctions, placeBid, watchListing, unwatchListing } = useWebSocket();
  const [bidAmount, setBidAmount] = useState('');
  const [isPlacingBid, setIsPlacingBid] = useState(false);
  const [bidHistory, setBidHistory] = useState([]);
  const [isWatching, setIsWatching] = useState(false);

  const listingId = listing.id;
  const auctionData = liveAuctions[listingId];
  const currentPrice = listing.price;
  const highestBid = auctionData?.current_high_bid || currentPrice;
  const isOwner = currentUser?.id === listing.seller_id;

  useEffect(() => {
    if (isConnected && listingId) {
      watchListing(listingId);
      setIsWatching(true);
    }

    return () => {
      if (isConnected && listingId) {
        unwatchListing(listingId);
        setIsWatching(false);
      }
    };
  }, [isConnected, listingId, watchListing, unwatchListing]);

  useEffect(() => {
    // Set minimum bid amount
    const minBid = highestBid + 1;
    if (!bidAmount || parseFloat(bidAmount) < minBid) {
      setBidAmount(minBid.toString());
    }
  }, [highestBid, bidAmount]);

  const handlePlaceBid = async () => {
    if (!bidAmount || isPlacingBid || isOwner) return;

    const bid = parseFloat(bidAmount);
    if (bid <= highestBid) {
      alert(`Bid must be higher than current high bid of €${highestBid}`);
      return;
    }

    setIsPlacingBid(true);

    try {
      // Place bid via WebSocket
      placeBid(listingId, bid);

      // Also track interaction for AI
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      await fetch(`${backendUrl}/v2/ai/interaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          listing_id: listingId,
          interaction_type: 'bid',
          context: { bid_amount: bid }
        })
      });

      // Add to local bid history
      setBidHistory(prev => [{
        id: `bid_${Date.now()}`,
        amount: bid,
        bidder: currentUser.username,
        timestamp: new Date().toISOString(),
        isOwn: true
      }, ...prev.slice(0, 9)]);

      if (onBidPlaced) {
        onBidPlaced(bid);
      }

    } catch (error) {
      console.error('Failed to place bid:', error);
      alert('Failed to place bid. Please try again.');
    }

    setIsPlacingBid(false);
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  if (isOwner) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="text-center">
          <div className="text-gray-500 mb-2">
            <span className="inline-block w-3 h-3 bg-gray-400 rounded-full mr-2"></span>
            Your Listing - Bidding Disabled
          </div>
          {auctionData && (
            <div className="text-sm text-gray-600">
              <p>Current High Bid: <strong>€{auctionData.current_high_bid}</strong></p>
              <p>Total Bids: {auctionData.bid_count}</p>
              {auctionData.last_bid_time && (
                <p>Last Bid: {formatTimeAgo(auctionData.last_bid_time)}</p>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      {/* Live Status Indicator */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
          <span className="text-sm font-medium text-gray-700">
            {isConnected ? 'Live Bidding' : 'Connecting...'}
          </span>
          {isWatching && (
            <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              Watching
            </span>
          )}
        </div>
        {auctionData && (
          <div className="text-xs text-gray-500">
            {auctionData.bid_count} bids
          </div>
        )}
      </div>

      {/* Current Price / High Bid */}
      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-1">Current High Bid</div>
        <div className="text-2xl font-bold text-gray-900">
          €{highestBid.toFixed(2)}
        </div>
        {auctionData && auctionData.last_bid_time && (
          <div className="text-xs text-gray-500">
            {formatTimeAgo(auctionData.last_bid_time)}
          </div>
        )}
      </div>

      {/* Bidding Form */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Your Bid (minimum: €{(highestBid + 1).toFixed(2)})
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">€</span>
            <input
              type="number"
              step="0.01"
              min={highestBid + 1}
              value={bidAmount}
              onChange={(e) => setBidAmount(e.target.value)}
              className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={`${(highestBid + 1).toFixed(2)}`}
              disabled={!isConnected || isPlacingBid}
            />
          </div>
        </div>

        <button
          onClick={handlePlaceBid}
          disabled={!isConnected || isPlacingBid || !bidAmount || parseFloat(bidAmount) <= highestBid}
          className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
            !isConnected || isPlacingBid || !bidAmount || parseFloat(bidAmount) <= highestBid
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isPlacingBid ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Placing Bid...
            </div>
          ) : (
            `Place Bid - €${bidAmount}`
          )}
        </button>
      </div>

      {/* Quick Bid Buttons */}
      <div className="mt-3 flex space-x-2">
        {[1, 5, 10, 25].map(increment => {
          const quickBid = highestBid + increment;
          return (
            <button
              key={increment}
              onClick={() => setBidAmount(quickBid.toString())}
              className="flex-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-1 px-2 rounded transition-colors"
              disabled={!isConnected}
            >
              +€{increment}
            </button>
          );
        })}
      </div>

      {/* Recent Bids */}
      {bidHistory.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Your Recent Bids</h4>
          <div className="space-y-1 max-h-24 overflow-y-auto">
            {bidHistory.map(bid => (
              <div key={bid.id} className="flex justify-between text-xs">
                <span className="text-gray-600">€{bid.amount}</span>
                <span className="text-gray-500">{formatTimeAgo(bid.timestamp)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection Status */}
      {!isConnected && (
        <div className="mt-3 text-center text-sm text-gray-500">
          <div className="animate-pulse">Reconnecting to live bidding...</div>
        </div>
      )}
    </div>
  );
};

export default LiveBiddingWidget;
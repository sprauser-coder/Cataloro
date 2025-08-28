<?php
/**
 * Plugin Name: Cataloro Marketplace Integration
 * Description: Integration plugin for Cataloro Marketplace with FastAPI backend
 * Version: 1.0.0
 * Author: Cataloro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class CataloroMarketplace {
    
    private $api_base_url = 'https://www.app.cataloro.com/api';
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_ajax_marketplace_api', array($this, 'handle_api_request'));
        add_action('wp_ajax_nopriv_marketplace_api', array($this, 'handle_api_request'));
        
        // Add shortcodes
        add_shortcode('marketplace_home', array($this, 'marketplace_home_shortcode'));
        add_shortcode('marketplace_login', array($this, 'marketplace_login_shortcode'));
        add_shortcode('marketplace_products', array($this, 'marketplace_products_shortcode'));
        add_shortcode('marketplace_cart', array($this, 'marketplace_cart_shortcode'));
        add_shortcode('marketplace_dashboard', array($this, 'marketplace_dashboard_shortcode'));
    }
    
    public function init() {
        // Create custom pages if they don't exist
        $this->create_marketplace_pages();
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script('marketplace-js', plugin_dir_url(__FILE__) . 'marketplace.js', array('jquery'), '1.0.0', true);
        wp_enqueue_style('marketplace-css', plugin_dir_url(__FILE__) . 'marketplace.css', array(), '1.0.0');
        
        // Localize script for AJAX
        wp_localize_script('marketplace-js', 'marketplace_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'api_base_url' => $this->api_base_url,
            'nonce' => wp_create_nonce('marketplace_nonce')
        ));
    }
    
    public function handle_api_request() {
        check_ajax_referer('marketplace_nonce', 'nonce');
        
        $endpoint = sanitize_text_field($_POST['endpoint']);
        $method = sanitize_text_field($_POST['method']);
        $data = isset($_POST['data']) ? $_POST['data'] : array();
        
        $response = $this->make_api_request($endpoint, $method, $data);
        
        wp_send_json($response);
    }
    
    private function make_api_request($endpoint, $method = 'GET', $data = array()) {
        $url = $this->api_base_url . $endpoint;
        
        $args = array(
            'method' => $method,
            'headers' => array(
                'Content-Type' => 'application/json',
            ),
            'timeout' => 30,
        );
        
        if ($method !== 'GET' && !empty($data)) {
            $args['body'] = json_encode($data);
        }
        
        // Add authorization header if user is logged in
        $token = $this->get_user_token();
        if ($token) {
            $args['headers']['Authorization'] = 'Bearer ' . $token;
        }
        
        $response = wp_remote_request($url, $args);
        
        if (is_wp_error($response)) {
            return array('error' => $response->get_error_message());
        }
        
        $body = wp_remote_retrieve_body($response);
        return json_decode($body, true);
    }
    
    private function get_user_token() {
        return get_user_meta(get_current_user_id(), 'marketplace_token', true);
    }
    
    private function set_user_token($token) {
        update_user_meta(get_current_user_id(), 'marketplace_token', $token);
    }
    
    public function marketplace_home_shortcode($atts) {
        ob_start();
        ?>
        <div id="marketplace-home">
            <div class="marketplace-hero">
                <h1>Discover Amazing Deals</h1>
                <p>Buy and sell with confidence on our marketplace</p>
                <div class="search-bar">
                    <input type="text" id="search-input" placeholder="Search for anything...">
                    <select id="category-filter">
                        <option value="">All Categories</option>
                    </select>
                </div>
            </div>
            <div id="product-listings" class="product-grid">
                <!-- Products will be loaded here via JavaScript -->
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function marketplace_login_shortcode($atts) {
        ob_start();
        ?>
        <div id="marketplace-auth">
            <div class="auth-toggle">
                <button id="login-tab" class="active">Login</button>
                <button id="register-tab">Register</button>
            </div>
            
            <form id="login-form" class="auth-form">
                <h2>Welcome Back</h2>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
            
            <form id="register-form" class="auth-form" style="display:none;">
                <h2>Join Marketplace</h2>
                <input type="email" name="email" placeholder="Email" required>
                <input type="text" name="username" placeholder="Username" required>
                <input type="text" name="full_name" placeholder="Full Name" required>
                <input type="password" name="password" placeholder="Password" required>
                <select name="role">
                    <option value="buyer">Buy items</option>
                    <option value="seller">Sell items</option>
                    <option value="both">Both buy and sell</option>
                </select>
                <input type="tel" name="phone" placeholder="Phone (Optional)">
                <input type="text" name="address" placeholder="Address (Optional)">
                <button type="submit">Create Account</button>
            </form>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function marketplace_products_shortcode($atts) {
        ob_start();
        ?>
        <div id="marketplace-products">
            <div class="filters">
                <select id="listing-type-filter">
                    <option value="">All Items</option>
                    <option value="fixed_price">Buy Now</option>
                    <option value="auction">Auctions</option>
                </select>
            </div>
            <div id="products-grid" class="products-container">
                <!-- Products will be loaded here -->
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function marketplace_cart_shortcode($atts) {
        ob_start();
        ?>
        <div id="marketplace-cart">
            <h2>Shopping Cart</h2>
            <div id="cart-items">
                <!-- Cart items will be loaded here -->
            </div>
            <div id="cart-summary" style="display:none;">
                <div class="total">Total: $<span id="cart-total">0.00</span></div>
                <button id="checkout-btn">Proceed to Checkout</button>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function marketplace_dashboard_shortcode($atts) {
        if (!is_user_logged_in()) {
            return '<p>Please log in to access your dashboard.</p>';
        }
        
        ob_start();
        ?>
        <div id="marketplace-dashboard">
            <div class="dashboard-tabs">
                <button class="tab-btn active" data-tab="orders">My Orders</button>
                <button class="tab-btn" data-tab="listings">My Listings</button>
                <button class="tab-btn" data-tab="profile">Profile</button>
            </div>
            
            <div id="orders-tab" class="tab-content active">
                <h3>My Orders</h3>
                <div id="user-orders"></div>
            </div>
            
            <div id="listings-tab" class="tab-content">
                <h3>My Listings</h3>
                <button id="create-listing-btn">Create New Listing</button>
                <div id="user-listings"></div>
            </div>
            
            <div id="profile-tab" class="tab-content">
                <h3>Profile Settings</h3>
                <div id="user-profile"></div>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    private function create_marketplace_pages() {
        $pages = array(
            'marketplace' => array(
                'title' => 'Marketplace',
                'content' => '[marketplace_home]'
            ),
            'marketplace-login' => array(
                'title' => 'Login',
                'content' => '[marketplace_login]'
            ),
            'marketplace-products' => array(
                'title' => 'Products',
                'content' => '[marketplace_products]'
            ),
            'marketplace-cart' => array(
                'title' => 'Shopping Cart',
                'content' => '[marketplace_cart]'
            ),
            'marketplace-dashboard' => array(
                'title' => 'Dashboard',
                'content' => '[marketplace_dashboard]'
            )
        );
        
        foreach ($pages as $slug => $page) {
            if (!get_page_by_path($slug)) {
                wp_insert_post(array(
                    'post_title' => $page['title'],
                    'post_content' => $page['content'],
                    'post_status' => 'publish',
                    'post_type' => 'page',
                    'post_name' => $slug
                ));
            }
        }
    }
}

// Initialize the plugin
new CataloroMarketplace();
?>
// Test script to debug Ad's Manager workflow
// Run this in browser console on the admin panel page

function testAdsManagerWorkflow() {
    console.log('=== AD\'S MANAGER WORKFLOW TEST ===');
    
    // Step 1: Check current localStorage
    const currentConfig = localStorage.getItem('cataloro_site_config');
    console.log('1. Current localStorage config:', currentConfig ? JSON.parse(currentConfig) : 'EMPTY');
    
    // Step 2: Simulate image upload
    console.log('2. Simulating image upload...');
    const testConfig = {
        adsManager: {
            browsePageAd: {
                active: true,
                image: '/uploads/cms/test_debug_image.png',
                description: 'Debug Test Image',
                runtime: '1 month',
                width: '300px',
                height: '600px',
                url: 'https://example.com/debug-test',
                clicks: 0
            }
        },
        heroSectionEnabled: true
    };
    
    localStorage.setItem('cataloro_site_config', JSON.stringify(testConfig));
    console.log('2. ✅ Test config saved to localStorage');
    
    // Step 3: Trigger ads config update event
    console.log('3. Dispatching adsConfigUpdated event...');
    window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
        detail: testConfig.adsManager 
    }));
    console.log('3. ✅ Event dispatched');
    
    // Step 4: Verify persistence
    setTimeout(() => {
        const verifyConfig = localStorage.getItem('cataloro_site_config');
        const parsed = verifyConfig ? JSON.parse(verifyConfig) : null;
        console.log('4. Verification check:');
        console.log('   - Config exists:', !!parsed);
        console.log('   - Has adsManager:', !!parsed?.adsManager);
        console.log('   - Has browse ad:', !!parsed?.adsManager?.browsePageAd);
        console.log('   - Image URL:', parsed?.adsManager?.browsePageAd?.image);
        
        if (parsed?.adsManager?.browsePageAd?.image === '/uploads/cms/test_debug_image.png') {
            console.log('4. ✅ SUCCESS: Image URL persisted correctly');
        } else {
            console.log('4. ❌ FAILURE: Image URL was lost or changed');
        }
    }, 1000);
    
    console.log('=== TEST COMPLETED - Check results above ===');
}

// Instructions
console.log('TO TEST: Run testAdsManagerWorkflow() in browser console');
console.log('USAGE: 1. Open Admin Panel → Administration → Ad\'s Manager');
console.log('       2. Open browser console (F12)');
console.log('       3. Run: testAdsManagerWorkflow()');
console.log('       4. Check results in console');

// Auto-run if on admin page
if (window.location.pathname.includes('/admin')) {
    console.log('Admin page detected - you can run testAdsManagerWorkflow() now');
}
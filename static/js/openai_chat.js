/**
 * Beacon OpenAI Chat Implementation
 * 
 * This script handles the chat interface for the Beacon AI real estate investment assistant
 * using OpenAI's API for more natural and dynamic conversations.
 */

// ===================================
// Conversation State Management
// ===================================

const conversationState = {
    messages: [],  // Stores the conversation history
    userInfo: {
        name: null,
        email: null,
        investment_strategy: null,
        boroughs: [],
        neighborhoods: [],
        property_types: [],
        min_budget: null,
        max_budget: null,
        risk_tolerance: null
    },
    showingProperty: false,
    showingEmailForm: false,
    waitingForResponse: false
};

// ===================================
// DOM Elements
// ===================================

// Chat interface elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userMessage');
const sendButton = document.getElementById('sendButton');

// Property card elements
const propertyCard = document.getElementById('propertyCard');
const propertyImage = document.getElementById('propertyImage');
const propertyTitle = document.getElementById('propertyTitle');
const propertyAddress = document.getElementById('propertyAddress');
const propertyBeds = document.getElementById('propertyBeds');
const propertyBaths = document.getElementById('propertyBaths');
const propertySize = document.getElementById('propertySize');
const propertyPrice = document.getElementById('propertyPrice');
const propertyDescription = document.getElementById('propertyDescription');
const requestMoreButton = document.getElementById('requestMoreProperties');

// Email form elements
const emailForm = document.getElementById('emailForm');
const userName = document.getElementById('userName');
const userEmail = document.getElementById('userEmail');
const submitEmailButton = document.getElementById('submitEmailButton');

// ===================================
// Chat Functions
// ===================================

// Initialize the chat with a welcome message
function initializeChat() {
    addBotMessage("Hi there! I'm Beacon, your NYC real estate investment assistant. I can help you find investment properties that match your goals and preferences. What kind of investment strategy are you interested in? (value, cashflow, growth, or luxury)");
}

// Process user message and get bot response
async function processUserMessage(message) {
    if (!message.trim()) return;
    
    // Add user message to UI
    addUserMessage(message);
    
    // Set waiting state
    conversationState.waitingForResponse = true;
    userInput.disabled = true;
    sendButton.disabled = true;
    
    try {
        // Send message to backend
        const response = await fetch('/api/openai_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                user_info: conversationState.userInfo
            })
        });
        
        const data = await response.json();
        
        // Update conversation state
        if (data.state) {
            // Update collected information if available
            if (data.state.collected_info) {
                const info = data.state.collected_info;
                
                // Update our local state with the backend's state
                if (info.name) conversationState.userInfo.name = info.name;
                if (info.email) conversationState.userInfo.email = info.email;
                if (info.investment_strategy) conversationState.userInfo.investment_strategy = info.investment_strategy;
                if (info.boroughs && info.boroughs.length) conversationState.userInfo.boroughs = info.boroughs;
                if (info.neighborhoods && info.neighborhoods.length) conversationState.userInfo.neighborhoods = info.neighborhoods;
                if (info.property_types && info.property_types.length) conversationState.userInfo.property_types = info.property_types;
                if (info.min_budget) conversationState.userInfo.min_budget = info.min_budget;
                if (info.max_budget) conversationState.userInfo.max_budget = info.max_budget;
                if (info.risk_tolerance) conversationState.userInfo.risk_tolerance = info.risk_tolerance;
            }
        }
        
        // Add bot response to UI
        addBotMessage(data.message);
        
        // Check if we've collected enough information to show property
        if (shouldShowProperty()) {
            getPropertyRecommendation();
        }
        
        // Check if we should show email form (if bot mentions email or recommendations)
        if (shouldShowEmailForm(data.message) && !conversationState.showingEmailForm) {
            showEmailForm();
        }
        
    } catch (error) {
        console.error('Error:', error);
        addBotMessage("I'm sorry, I'm having trouble connecting to our system. Please try again in a moment.");
    } finally {
        // Reset UI state
        conversationState.waitingForResponse = false;
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Add user message to chat
function addUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message user-message';
    messageElement.innerHTML = `<div class="message-content">${message}</div>`;
    chatMessages.appendChild(messageElement);
    
    // Save to conversation history
    conversationState.messages.push({
        role: 'user',
        content: message
    });
    
    // Scroll to bottom
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message bot-message';
    
    // Create avatar element
    const avatar = document.createElement('div');
    avatar.className = 'bot-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    // Create content element with typing effect
    const content = document.createElement('div');
    content.className = 'message-content';
    messageElement.appendChild(avatar);
    messageElement.appendChild(content);
    
    chatMessages.appendChild(messageElement);
    scrollToBottom();
    
    // Add typing effect
    let i = 0;
    const speed = 20; // typing speed in ms
    const text = message;
    
    function typeWriter() {
        if (i < text.length) {
            content.innerHTML += text.charAt(i);
            i++;
            scrollToBottom();
            setTimeout(typeWriter, speed);
        }
    }
    
    typeWriter();
    
    // Save to conversation history
    conversationState.messages.push({
        role: 'assistant',
        content: message
    });
}

// Scroll chat to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Check if we have enough information to show a property
function shouldShowProperty() {
    const info = conversationState.userInfo;
    
    // If we're already showing a property, don't show another one
    if (conversationState.showingProperty) return false;
    
    // Check if we have the minimum required information
    return (
        info.investment_strategy && 
        info.boroughs.length > 0 &&
        !conversationState.showingProperty
    );
}

// Check if the bot message suggests we should show email form
function shouldShowEmailForm(message) {
    const lowerMessage = message.toLowerCase();
    
    return (
        (lowerMessage.includes('email') && 
         (lowerMessage.includes('send') || lowerMessage.includes('more'))) ||
        (lowerMessage.includes('property') && 
         lowerMessage.includes('recommend'))
    );
}

// Get property recommendation from backend
async function getPropertyRecommendation() {
    try {
        // Debug: Log what's being sent to the API
        console.log('Sending to API:', {
            investment_strategy: conversationState.userInfo.investment_strategy,
            boroughs: conversationState.userInfo.boroughs,
            property_types: conversationState.userInfo.property_types
        });
        
        const response = await fetch('/api/get_property_recommendation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                investment_strategy: conversationState.userInfo.investment_strategy,
                boroughs: conversationState.userInfo.boroughs,
                property_types: conversationState.userInfo.property_types
            })
        });
        
        // Debug: Log the response status
        console.log('API response status:', response.status);
        
        if (!response.ok) {
            throw new Error('Failed to get property recommendation');
        }
        
        const property = await response.json();
        // Debug: Log the property data
        console.log('Property data received:', property);
        
        displayProperty(property);
        
    } catch (error) {
        console.error('Error getting property recommendation:', error);
    }
}

// Display property card
function displayProperty(property) {
    // If we have a property to display
    if (property && !property.error) {
        // Update property card elements
        propertyTitle.textContent = property.property_name || "NYC Investment Property";
        propertyAddress.textContent = `${property.neighborhood}, ${property.borough}` || "";
        propertyBeds.innerHTML = `<i class="fas fa-bed"></i> ${property.bedrooms} beds`;
        propertyBaths.innerHTML = `<i class="fas fa-bath"></i> ${property.bathrooms} baths`;
        propertySize.innerHTML = `<i class="fas fa-ruler-combined"></i> ${property.square_feet} sq ft`;
        propertyPrice.textContent = formatCurrency(property.price);
        propertyDescription.textContent = property.description || "";
        
        // Set property image if available
        if (property.image_url) {
            propertyImage.src = property.image_url;
        } else {
            propertyImage.src = "/static/images/property-placeholder.jpg";
        }
        
        // Show property card
        propertyCard.style.display = 'flex';
        conversationState.showingProperty = true;
        
        // Scroll to property card
        setTimeout(() => {
            propertyCard.scrollIntoView({ behavior: 'smooth' });
        }, 500);
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    }).format(amount);
}

// Show email collection form
function showEmailForm() {
    emailForm.style.display = 'block';
    conversationState.showingEmailForm = true;
    
    // Pre-fill name and email if available
    if (conversationState.userInfo.name) {
        userName.value = conversationState.userInfo.name;
    }
    
    if (conversationState.userInfo.email) {
        userEmail.value = conversationState.userInfo.email;
    }
    
    // Scroll to email form
    setTimeout(() => {
        emailForm.scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

// Submit user profile
async function submitUserProfile() {
    // Validate email
    if (!userEmail.value || !isValidEmail(userEmail.value)) {
        alert('Please enter a valid email address');
        return;
    }
    
    // Update user info
    conversationState.userInfo.name = userName.value;
    conversationState.userInfo.email = userEmail.value;
    
    try {
        const response = await fetch('/api/submit_profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(conversationState.userInfo)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Hide email form
            emailForm.style.display = 'none';
            
            // Add success message to chat
            addBotMessage(`Thanks ${userName.value}! We've sent property recommendations to ${userEmail.value}. Is there anything else you'd like to know about NYC real estate investments?`);
        } else {
            addBotMessage("I'm sorry, we couldn't save your information. Please try again.");
        }
        
    } catch (error) {
        console.error('Error submitting user profile:', error);
        addBotMessage("I'm sorry, we're experiencing technical difficulties. Please try again later.");
    }
}

// Validate email format
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ===================================
// Event Listeners
// ===================================

// Send button click
sendButton.addEventListener('click', () => {
    const message = userInput.value.trim();
    if (message && !conversationState.waitingForResponse) {
        processUserMessage(message);
        userInput.value = '';
    }
});

// Enter key press in input field
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !conversationState.waitingForResponse) {
        const message = userInput.value.trim();
        if (message) {
            processUserMessage(message);
            userInput.value = '';
        }
    }
});

// Request more properties button
requestMoreButton.addEventListener('click', () => {
    showEmailForm();
    addBotMessage("Great! To send you more properties like this, I'll need your contact information.");
});

// Submit email button
submitEmailButton.addEventListener('click', submitUserProfile);

// ===================================
// Initialize
// ===================================

// Start the chat when the DOM is loaded
document.addEventListener('DOMContentLoaded', initializeChat); 
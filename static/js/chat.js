// Conversation state object
let conversationState = {
    step: 'welcome', // Current step in the conversation
    investment_strategy: '',
    boroughs: [],
    neighborhoods: [],
    property_types: [],
    min_budget: null,
    max_budget: null,
    risk_tolerance: '',
    name: '',
    email: '',
    collectedInfo: {}, // For tracking what information we've collected
    missingInfo: [], // For tracking what information we still need
    history: [] // For tracking conversation history
};

// Main knowledge areas and goals
const chatbotGoals = {
    introduceBeacon: false,
    understandInvestmentStrategy: false,
    captureLocationPreferences: false,
    determinePropertyTypes: false,
    establishBudget: false,
    assessRiskTolerance: false,
    presentRecommendation: false,
    obtainContactInfo: false
};

// Domain knowledge for the AI
const domainKnowledge = {
    investmentStrategies: {
        'value': 'Focuses on finding undervalued properties with potential for appreciation.',
        'cashflow': 'Prioritizes consistent rental income and positive cash flow.',
        'growth': 'Aims for long-term appreciation in developing or up-and-coming areas.',
        'luxury': 'Targets high-end properties in premium locations.'
    },
    boroughs: {
        'Manhattan': 'The most densely populated borough with the highest property values.',
        'Brooklyn': 'Known for cultural diversity and rapidly appreciating neighborhoods.',
        'Queens': 'The largest borough by area with a mix of housing options.',
        'Bronx': 'The most affordable borough with emerging investment opportunities.',
        'Staten Island': 'The most suburban-like borough with lower density housing.'
    },
    popularNeighborhoods: {
        'Manhattan': ['Upper West Side', 'Upper East Side', 'Chelsea', 'Greenwich Village', 'Tribeca', 'Harlem'],
        'Brooklyn': ['Williamsburg', 'Park Slope', 'DUMBO', 'Brooklyn Heights', 'Bushwick'],
        'Queens': ['Astoria', 'Long Island City', 'Forest Hills', 'Flushing', 'Jamaica'],
        'Bronx': ['Riverdale', 'Mott Haven', 'Fordham', 'Pelham Bay'],
        'Staten Island': ['St. George', 'Tottenville', 'Great Kills']
    },
    propertyTypes: {
        'Condo': 'Individually owned units in a shared building with less restrictions than co-ops.',
        'Co-op': 'Shares in a corporation that owns the building; typically lower prices but stricter rules.',
        'Townhouse': 'Multi-story attached homes, often with rental income potential.',
        'Multi-family': 'Buildings with multiple separate living units, good for rental income.',
        'Single-family': 'Standalone houses, less common in NYC except in outer boroughs.'
    },
    riskLevels: {
        'low': 'Established neighborhoods with stable property values and strong rental demand.',
        'medium': 'Mix of established areas and up-and-coming neighborhoods with good appreciation potential.',
        'high': 'Emerging neighborhoods with higher potential returns but greater uncertainty.'
    }
};

// DOM elements
const chatContainer = document.getElementById('chat-container');
const messageContainer = document.getElementById('message-container');
const userInputContainer = document.getElementById('user-input-container');
const loadingIndicator = document.getElementById('loading-indicator');

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    startConversation();
});

// Start the conversation
function startConversation() {
    displayBotMessage("👋 Welcome to Beacon! I'm your NYC real estate investment assistant. I help investors like you find properties that match your investment strategy in the NYC market. Would you like to discover how Beacon can help you find your next investment property?");
    
    displayOptions([
        { text: "Yes, tell me more", value: "yes" },
        { text: "No thanks", value: "no" }
    ]);
}

// Display a bot message
function displayBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message bot-message';
    messageElement.innerHTML = message;
    messageContainer.appendChild(messageElement);
    scrollToBottom();
}

// Display a user message
function displayUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message user-message';
    messageElement.textContent = message;
    messageContainer.appendChild(messageElement);
    scrollToBottom();
    
    // Add to conversation history
    conversationState.history.push({
        role: 'user',
        message: message
    });
}

// Process user's message through our AI logic
async function processUserMessage(message) {
    displayUserMessage(message);
    
    // Show typing indicator
    showLoading();
    
    try {
        // Analyze the message and determine next steps
        await analyzeAndRespond(message);
    } catch (error) {
        console.error('Error processing message:', error);
        displayBotMessage("I'm sorry, I encountered an error processing your message. Let's try a different approach.");
    } finally {
        hideLoading();
    }
}

// Display clickable options
function displayOptions(options) {
    clearUserInput();
    
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'options-container';
    
    options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'option-button';
        button.textContent = option.text;
        button.addEventListener('click', () => {
            processUserMessage(option.text);
        });
        optionsContainer.appendChild(button);
    });
    
    userInputContainer.appendChild(optionsContainer);
}

// Display text input for free-form responses
function displayTextInput(placeholder = "Type your message...") {
    clearUserInput();
    
    const inputContainer = document.createElement('div');
    inputContainer.className = 'input-container';
    
    const textInput = document.createElement('input');
    textInput.type = 'text';
    textInput.placeholder = placeholder;
    textInput.className = 'text-input';
    
    textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const message = textInput.value.trim();
            if (message) {
                processUserMessage(message);
            }
        }
    });
    
    const sendButton = document.createElement('button');
    sendButton.className = 'submit-button';
    sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    sendButton.addEventListener('click', () => {
        const message = textInput.value.trim();
        if (message) {
            processUserMessage(message);
        }
    });
    
    inputContainer.appendChild(textInput);
    inputContainer.appendChild(sendButton);
    userInputContainer.appendChild(inputContainer);
    
    // Focus the input field
    setTimeout(() => {
        textInput.focus();
    }, 100);
}

// Core AI processing function
async function analyzeAndRespond(userMessage) {
    // Add to conversation history
    conversationState.history.push({
        role: 'user',
        message: userMessage
    });
    
    // Convert to lowercase for easier matching
    const messageLower = userMessage.toLowerCase();
    
    // Check conversation stage
    if (conversationState.step === 'welcome') {
        if (messageLower.includes('yes') || messageLower.includes('sure') || messageLower.includes('tell me more')) {
            chatbotGoals.introduceBeacon = true;
            conversationState.step = 'introduction';
            
            displayBotMessage("Great! Beacon specializes in finding NYC properties that match your specific investment criteria. I'll ask you a few questions to understand what you're looking for, then provide a property recommendation based on your preferences.");
            
            setTimeout(() => {
                displayBotMessage("First, what's your primary investment strategy? Are you looking for value investments (undervalued properties with upside potential), cash flow (rental income focus), growth/appreciation (long-term value growth), or luxury/premium properties?");
                conversationState.step = 'investment_strategy';
                displayTextInput("E.g., I'm interested in cash flow properties...");
            }, 1000);
        } else {
            displayBotMessage("No problem! If you change your mind about finding NYC investment properties, feel free to come back. Have a great day! 👋");
            conversationState.step = 'ended';
        }
    }
    else if (conversationState.step === 'investment_strategy') {
        // Extract investment strategy from user message
        let detectedStrategy = null;
        
        if (messageLower.includes('value') || messageLower.includes('undervalued')) {
            detectedStrategy = 'value';
        } else if (messageLower.includes('cash') || messageLower.includes('rental') || messageLower.includes('income')) {
            detectedStrategy = 'cashflow';
        } else if (messageLower.includes('growth') || messageLower.includes('appreciation') || messageLower.includes('long-term')) {
            detectedStrategy = 'growth';
        } else if (messageLower.includes('luxury') || messageLower.includes('premium') || messageLower.includes('high-end')) {
            detectedStrategy = 'luxury';
        }
        
        if (detectedStrategy) {
            conversationState.investment_strategy = detectedStrategy;
            chatbotGoals.understandInvestmentStrategy = true;
            
            displayBotMessage(`Great choice! ${domainKnowledge.investmentStrategies[detectedStrategy]} Now, which NYC boroughs are you interested in exploring? You can select multiple.`);
            
            // Show borough options but also allow typing
            displayOptions([
                { text: "Manhattan", value: "Manhattan" },
                { text: "Brooklyn", value: "Brooklyn" },
                { text: "Queens", value: "Queens" },
                { text: "The Bronx", value: "Bronx" },
                { text: "Staten Island", value: "Staten Island" },
                { text: "All boroughs", value: "all" }
            ]);
            
            conversationState.step = 'boroughs';
        } else {
            displayBotMessage("I'm not sure I understood your investment strategy preference. Could you clarify if you're looking for value investments, cash flow properties, growth/appreciation, or luxury properties?");
        }
    }
    else if (conversationState.step === 'boroughs') {
        // Extract borough preferences
        const allBoroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'];
        let selectedBoroughs = [];
        
        if (messageLower.includes('all') || messageLower.includes('any') || messageLower.includes('every')) {
            selectedBoroughs = [...allBoroughs];
        } else {
            // Check for each borough
            if (messageLower.includes('manhattan')) selectedBoroughs.push('Manhattan');
            if (messageLower.includes('brooklyn')) selectedBoroughs.push('Brooklyn');
            if (messageLower.includes('queens')) selectedBoroughs.push('Queens');
            if (messageLower.includes('bronx')) selectedBoroughs.push('Bronx');
            if (messageLower.includes('staten')) selectedBoroughs.push('Staten Island');
        }
        
        if (selectedBoroughs.length > 0) {
            conversationState.boroughs = selectedBoroughs;
            chatbotGoals.captureLocationPreferences = true;
            
            if (selectedBoroughs.length === 1) {
                // Suggest neighborhoods from that borough
                const borough = selectedBoroughs[0];
                const neighborhoodsList = domainKnowledge.popularNeighborhoods[borough].join(', ');
                
                displayBotMessage(`${borough} is an excellent choice! Popular neighborhoods there include ${neighborhoodsList}. Are there specific neighborhoods you're interested in? (This is optional, you can also say "no preference")`);
            } else {
                displayBotMessage(`Great choices! Are there specific neighborhoods within ${selectedBoroughs.join(', ')} that you're interested in? (This is optional, you can also say "no preference")`);
            }
            
            conversationState.step = 'neighborhoods';
            displayTextInput("E.g., Upper West Side, Williamsburg, or no preference");
        } else {
            displayBotMessage("I didn't catch which boroughs you're interested in. Could you specify which NYC boroughs you'd like to focus on? Manhattan, Brooklyn, Queens, The Bronx, Staten Island, or all of them?");
        }
    }
    else if (conversationState.step === 'neighborhoods') {
        if (messageLower.includes('no') || messageLower.includes('any') || messageLower.includes("doesn't matter")) {
            conversationState.neighborhoods = [];
            displayBotMessage("No problem! Let's move on to property types. What kinds of properties are you interested in? Condos, co-ops, townhouses, multi-family buildings, or single-family homes?");
        } else {
            // Extract neighborhood names
            conversationState.neighborhoods = userMessage.split(',').map(n => n.trim());
            displayBotMessage(`Great! I've noted your interest in ${conversationState.neighborhoods.join(', ')}. Now, what types of properties are you looking for? Condos, co-ops, townhouses, multi-family buildings, or single-family homes?`);
        }
        
        conversationState.step = 'property_types';
        displayOptions([
            { text: "Condos", value: "Condo" },
            { text: "Co-ops", value: "Co-op" },
            { text: "Townhouses", value: "Townhouse" },
            { text: "Multi-family buildings", value: "Multi-family" },
            { text: "Single-family homes", value: "Single-family" },
            { text: "All property types", value: "all" }
        ]);
    }
    else if (conversationState.step === 'property_types') {
        // Extract property types
        const allTypes = ['Condo', 'Co-op', 'Townhouse', 'Multi-family', 'Single-family'];
        let selectedTypes = [];
        
        if (messageLower.includes('all') || messageLower.includes('any') || messageLower.includes('every')) {
            selectedTypes = [...allTypes];
        } else {
            // Check for each property type
            if (messageLower.includes('condo')) selectedTypes.push('Condo');
            if (messageLower.includes('co-op') || messageLower.includes('coop')) selectedTypes.push('Co-op');
            if (messageLower.includes('town') || messageLower.includes('brownstone')) selectedTypes.push('Townhouse');
            if (messageLower.includes('multi') || messageLower.includes('multiple') || messageLower.includes('units')) selectedTypes.push('Multi-family');
            if (messageLower.includes('single') || messageLower.includes('house')) selectedTypes.push('Single-family');
        }
        
        if (selectedTypes.length > 0) {
            conversationState.property_types = selectedTypes;
            chatbotGoals.determinePropertyTypes = true;
            
            displayBotMessage("What's your investment budget range? Please share your minimum and maximum budget in dollars.");
            conversationState.step = 'budget';
            displayTextInput("E.g., Between $500,000 and $2,000,000");
        } else {
            displayBotMessage("I didn't catch which property types you're interested in. Could you specify from condos, co-ops, townhouses, multi-family buildings, or single-family homes?");
        }
    }
    else if (conversationState.step === 'budget') {
        // Extract budget information
        let minBudget = null;
        let maxBudget = null;
        
        // Remove commas, spaces, and "$" for easier parsing
        const cleaned = userMessage.replace(/[$,\s]/g, '');
        
        // Look for patterns like "500000 to 2000000" or "between 500000 and 2000000"
        const budgetPattern = /(\d+)(?:\s*(?:to|and|-|through)\s*)(\d+)/i;
        const match = cleaned.match(budgetPattern);
        
        if (match) {
            minBudget = parseInt(match[1]);
            maxBudget = parseInt(match[2]);
        } else {
            // Try to find any numbers in the text
            const numbers = cleaned.match(/\d+/g);
            if (numbers && numbers.length >= 2) {
                // Assume the first two numbers are min and max
                minBudget = parseInt(numbers[0]);
                maxBudget = parseInt(numbers[1]);
            } else if (numbers && numbers.length === 1) {
                // If only one number, assume it's the max budget
                maxBudget = parseInt(numbers[0]);
                minBudget = Math.floor(maxBudget * 0.5); // Default min to 50% of max
            }
        }
        
        if (minBudget && maxBudget) {
            conversationState.min_budget = minBudget;
            conversationState.max_budget = maxBudget;
            chatbotGoals.establishBudget = true;
            
            const formattedMin = minBudget.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
            const formattedMax = maxBudget.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
            
            displayBotMessage(`Thank you! I've noted your budget range of ${formattedMin} to ${formattedMax}. How would you describe your risk tolerance for NYC real estate investments? Low risk (established neighborhoods, stable returns), medium risk (mix of established and emerging areas), or high risk (emerging neighborhoods, higher potential returns)?`);
            
            conversationState.step = 'risk_tolerance';
            displayOptions([
                { text: "Low risk", value: "low" },
                { text: "Medium risk", value: "medium" },
                { text: "High risk", value: "high" }
            ]);
        } else {
            displayBotMessage("I couldn't determine your budget range from that. Could you specify your minimum and maximum budget in a format like '$500,000 to $2,000,000'?");
        }
    }
    else if (conversationState.step === 'risk_tolerance') {
        let riskLevel = null;
        
        if (messageLower.includes('low')) {
            riskLevel = 'low';
        } else if (messageLower.includes('medium') || messageLower.includes('moderate') || messageLower.includes('mid')) {
            riskLevel = 'medium';
        } else if (messageLower.includes('high')) {
            riskLevel = 'high';
        }
        
        if (riskLevel) {
            conversationState.risk_tolerance = riskLevel;
            chatbotGoals.assessRiskTolerance = true;
            
            displayBotMessage(`Thanks for sharing your investment criteria. Based on your ${conversationState.investment_strategy} strategy, preferences in ${conversationState.boroughs.join(', ')}, budget, and ${riskLevel} risk tolerance, let me search for a property recommendation for you...`);
            
            // Simulate searching
            showLoading();
            setTimeout(() => {
                hideLoading();
                displayBotMessage("I've found a property that matches your criteria. Would you like to see it?");
                
                displayOptions([
                    { text: "Yes, show me", value: "yes" },
                    { text: "No thanks", value: "no" }
                ]);
                
                conversationState.step = 'show_recommendation';
            }, 2000);
        } else {
            displayBotMessage("I didn't catch your risk tolerance preference. Are you looking for low risk (established neighborhoods), medium risk (mix of established and emerging areas), or high risk (emerging neighborhoods with higher potential returns)?");
        }
    }
    else if (conversationState.step === 'show_recommendation') {
        if (messageLower.includes('yes') || messageLower.includes('show') || messageLower.includes('sure')) {
            await showPropertyRecommendation();
            chatbotGoals.presentRecommendation = true;
            
            setTimeout(() => {
                displayBotMessage("Would you like to receive weekly NYC real estate investment recommendations tailored to your preferences like this one?");
                displayOptions([
                    { text: "Yes, sign me up", value: "yes" },
                    { text: "No thanks", value: "no" }
                ]);
                conversationState.step = 'newsletter';
            }, 1000);
        } else {
            displayBotMessage("No problem. Would you like to receive weekly NYC real estate investment recommendations tailored to your preferences?");
            displayOptions([
                { text: "Yes, sign me up", value: "yes" },
                { text: "No thanks", value: "no" }
            ]);
            conversationState.step = 'newsletter';
        }
    }
    else if (conversationState.step === 'newsletter') {
        if (messageLower.includes('yes') || messageLower.includes('sign') || messageLower.includes('sure')) {
            displayBotMessage("Great! Please enter your name and email to receive personalized property recommendations:");
            
            // Create form for name and email
            const formContainer = document.createElement('div');
            formContainer.className = 'form-container';
            
            // Name input
            const nameLabel = document.createElement('label');
            nameLabel.textContent = 'Your Name';
            const nameInput = document.createElement('input');
            nameInput.type = 'text';
            nameInput.placeholder = 'Enter your name';
            nameInput.className = 'form-input';
            
            // Email input
            const emailLabel = document.createElement('label');
            emailLabel.textContent = 'Email Address';
            const emailInput = document.createElement('input');
            emailInput.type = 'email';
            emailInput.placeholder = 'Enter your email';
            emailInput.className = 'form-input';
            
            // Submit button
            const submitButton = document.createElement('button');
            submitButton.className = 'submit-button';
            submitButton.textContent = 'Subscribe';
            submitButton.addEventListener('click', async () => {
                const name = nameInput.value.trim();
                const email = emailInput.value.trim();
                
                if (!name) {
                    alert('Please enter your name.');
                    return;
                }
                
                if (!email || !validateEmail(email)) {
                    alert('Please enter a valid email address.');
                    return;
                }
                
                conversationState.name = name;
                conversationState.email = email;
                
                displayUserMessage(`${name} (${email})`);
                chatbotGoals.obtainContactInfo = true;
                
                // Show loading indicator
                showLoading();
                
                try {
                    // Submit profile to server
                    const profileData = {
                        name: conversationState.name,
                        email: conversationState.email,
                        investment_strategy: conversationState.investment_strategy,
                        boroughs: conversationState.boroughs,
                        neighborhoods: conversationState.neighborhoods,
                        property_types: conversationState.property_types,
                        min_budget: conversationState.min_budget,
                        max_budget: conversationState.max_budget,
                        risk_tolerance: conversationState.risk_tolerance
                    };
                    
                    const response = await fetch('/api/submit_profile', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(profileData)
                    });
                    
                    const result = await response.json();
                    
                    if (!result.success) {
                        throw new Error(result.error || 'Failed to save profile');
                    }
                    
                    displayBotMessage(`Thank you, ${name}! You're now subscribed to receive personalized NYC property recommendations. You'll get your first email update soon!`);
                    
                    setTimeout(() => {
                        displayBotMessage("Is there anything else you'd like to know about Beacon or NYC real estate investments?");
                        conversationState.step = 'followup';
                        displayTextInput("Ask me anything or type 'no' to end the conversation");
                    }, 1000);
                    
                } catch (error) {
                    console.error('Error submitting profile:', error);
                    displayBotMessage("I'm sorry, there was an error saving your information. Please try again.");
                } finally {
                    hideLoading();
                }
            });
            
            // Add elements to form
            formContainer.appendChild(nameLabel);
            formContainer.appendChild(nameInput);
            formContainer.appendChild(emailLabel);
            formContainer.appendChild(emailInput);
            formContainer.appendChild(submitButton);
            
            // Clear and add form
            clearUserInput();
            userInputContainer.appendChild(formContainer);
            
            conversationState.step = 'collecting_info';
            
        } else {
            displayBotMessage("No problem! If you change your mind about receiving NYC property recommendations, you can always come back and sign up later.");
            
            setTimeout(() => {
                displayBotMessage("Is there anything else you'd like to know about Beacon or NYC real estate investments?");
                conversationState.step = 'followup';
                displayTextInput("Ask me anything or type 'no' to end the conversation");
            }, 1000);
        }
    }
    else if (conversationState.step === 'followup' || conversationState.step === 'free_chat') {
        if (messageLower.includes('no') || messageLower.includes('goodbye') || messageLower.includes('bye') || messageLower.includes('that')) {
            displayBotMessage("Thanks for chatting with Beacon! Feel free to return anytime you're looking for NYC real estate investment opportunities. Have a great day! 👋");
            conversationState.step = 'ended';
        } else if (messageLower.includes('investment') || messageLower.includes('strategy')) {
            displayBotMessage("Beacon focuses on four main NYC investment strategies:<br><br>" +
                "<strong>Value Investing:</strong> Finding undervalued properties with upside potential in established or improving areas.<br><br>" +
                "<strong>Cash Flow:</strong> Properties that generate consistent rental income from day one, often in outer boroughs.<br><br>" +
                "<strong>Growth/Appreciation:</strong> Areas expected to see significant price appreciation over 5-10 years.<br><br>" +
                "<strong>Luxury:</strong> Premium properties in exclusive neighborhoods that hold value through market cycles.<br><br>" +
                "Do you have questions about any specific strategy?");
            
            conversationState.step = 'free_chat';
            displayTextInput();
        } else if (messageLower.includes('neighborhood') || messageLower.includes('area') || messageLower.includes('location')) {
            displayBotMessage("NYC has incredibly diverse neighborhoods across its five boroughs. Some investment hotspots currently include:<br><br>" +
                "<strong>Manhattan:</strong> Hudson Yards, Lower East Side, Harlem<br>" +
                "<strong>Brooklyn:</strong> Bushwick, Crown Heights, Sunset Park<br>" +
                "<strong>Queens:</strong> Long Island City, Jamaica, Flushing<br>" +
                "<strong>Bronx:</strong> Mott Haven, Melrose, Fordham<br>" +
                "<strong>Staten Island:</strong> St. George, Stapleton<br><br>" +
                "Each area has different investment characteristics. Is there a specific borough you'd like to know more about?");
            
            conversationState.step = 'free_chat';
            displayTextInput();
        } else {
            // General response for other questions
            displayBotMessage("That's an interesting question! While I'm focused on helping you find NYC investment properties, I'd be happy to connect you with a Beacon specialist who can provide more detailed information on that topic. Would you like to sign up for our newsletter to get more insights?");
            
            conversationState.step = 'free_chat';
            displayTextInput();
        }
    }
    else {
        // Fallback for any other state
        displayBotMessage("I'm not sure I understood. Could you rephrase your question or let me know what you'd like to do next?");
        displayTextInput();
    }
    
    // Add AI response to history
    conversationState.history.push({
        role: 'assistant',
        message: document.querySelector('.bot-message:last-child').innerHTML
    });
}

// Show property recommendation
async function showPropertyRecommendation() {
    showLoading();
    
    try {
        // Request property recommendation from server
        const response = await fetch('/api/get_property_recommendation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                investment_strategy: conversationState.investment_strategy,
                boroughs: conversationState.boroughs,
                property_types: conversationState.property_types
            })
        });
        
        const property = await response.json();
        
        if (response.status !== 200) {
            throw new Error(property.error || 'Failed to get recommendation');
        }
        
        // Create property card HTML
        const propertyCard = `
            <div class="property-card">
                <h3>${property.property_name}</h3>
                <div class="property-details">
                    <p class="property-location">${property.neighborhood}, ${property.borough}</p>
                    <p class="property-type">${property.property_type} | ${property.bedrooms} BR | ${property.bathrooms} BA | ${property.square_feet} sq ft</p>
                    <p class="property-price">$${property.price.toLocaleString()}</p>
                    <p class="property-description">${property.description}</p>
                    <div class="property-investment">
                        <p>Investment Strategy: <strong>${property.investment_strategy.toUpperCase()}</strong></p>
                        <p>ROI Potential: <strong>${property.roi_potential}%</strong></p>
                        <p>Risk Level: <strong>${property.risk_level.toUpperCase()}</strong></p>
                    </div>
                </div>
            </div>
            <p>This property aligns well with your ${conversationState.investment_strategy} strategy and ${conversationState.risk_tolerance} risk tolerance. It's located in ${property.neighborhood}, which is ${getNeighborhoodDescription(property.neighborhood, property.borough)}.</p>
            <p>This is just one example of what Beacon can find for you. Our full platform analyzes hundreds of NYC properties to find the best matches for your specific criteria.</p>
        `;
        
        // Display recommendation
        displayBotMessage(propertyCard);
        return true;
    } catch (error) {
        console.error('Error getting property recommendation:', error);
        displayBotMessage("I'm sorry, I couldn't find a matching property at the moment. This sometimes happens when we have very specific criteria. I'd be happy to connect you with a Beacon specialist who can conduct a more thorough search.");
        return false;
    } finally {
        hideLoading();
    }
}

// Get a description of a neighborhood (simplified version)
function getNeighborhoodDescription(neighborhood, borough) {
    const neighborhoodDescriptions = {
        'Upper West Side': 'a family-friendly area with beautiful brownstones and proximity to Central Park',
        'Greenwich Village': 'a historic neighborhood known for its cultural significance and charming streets',
        'Tribeca': 'an upscale neighborhood with converted industrial lofts and high-end amenities',
        'Williamsburg': 'a trendy area with a vibrant arts scene and excellent dining options',
        'Park Slope': 'a family-friendly neighborhood with beautiful brownstones near Prospect Park',
        'Dumbo': 'a former industrial area with stunning Manhattan views and luxury conversions',
        'Astoria': 'a diverse neighborhood with excellent food and reasonable prices',
        'Long Island City': 'a rapidly developing area with new high-rises and Manhattan views',
        'Forest Hills': 'an established residential neighborhood with a mix of housing options',
        'Riverdale': 'an upscale residential area with a suburban feel',
        'Mott Haven': 'an emerging area with historic architecture and development potential',
        'St. George': 'a neighborhood with ferry access to Manhattan and ongoing development'
    };
    
    return neighborhoodDescriptions[neighborhood] || `a promising area in ${borough} with good investment potential`;
}

// Helper functions
function clearUserInput() {
    userInputContainer.innerHTML = '';
}

function scrollToBottom() {
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function showLoading() {
    loadingIndicator.style.display = 'block';
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

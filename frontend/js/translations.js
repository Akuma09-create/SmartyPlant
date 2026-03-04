/**
 * Translation module for Smart Plant Health Assistant
 * Supports English (en), Hindi (hi), and Marathi (mr)
 */

const TRANSLATIONS = {
    // Common UI Labels
    app_name: {
        en: 'Smart Plant Health Assistant',
        hi: 'स्मार्ट पौधा स्वास्थ्य सहायक',
        mr: 'स्मार्ट वनस्पती आरोग्य सहाय्यक'
    },
    welcome: {
        en: 'Welcome',
        hi: 'स्वागत है',
        mr: 'स्वागत आहे'
    },
    login: {
        en: 'Login',
        hi: 'लॉगिन',
        mr: 'लॉगिन'
    },
    register: {
        en: 'Register',
        hi: 'पंजीकरण',
        mr: 'नोंदणी'
    },
    logout: {
        en: 'Logout',
        hi: 'लॉगआउट',
        mr: 'लॉगआउट'
    },
    dashboard: {
        en: 'Dashboard',
        hi: 'डैशबोर्ड',
        mr: 'डॅशबोर्ड'
    },
    my_plants: {
        en: 'My Plants',
        hi: 'मेरे पौधे',
        mr: 'माझी रोपे'
    },
    history: {
        en: 'History',
        hi: 'इतिहास',
        mr: 'इतिहास'
    },
    settings: {
        en: 'Settings',
        hi: 'सेटिंग्स',
        mr: 'सेटिंग्ज'
    },
    notifications: {
        en: 'Notifications',
        hi: 'सूचनाएं',
        mr: 'सूचना'
    },
    analyze: {
        en: 'Analyze',
        hi: 'विश्लेषण करें',
        mr: 'विश्लेषण करा'
    },
    upload: {
        en: 'Upload',
        hi: 'अपलोड करें',
        mr: 'अपलोड करा'
    },
    capture: {
        en: 'Capture',
        hi: 'कैप्चर करें',
        mr: 'कॅप्चर करा'
    },
    submit: {
        en: 'Submit',
        hi: 'जमा करें',
        mr: 'सबमिट करा'
    },
    cancel: {
        en: 'Cancel',
        hi: 'रद्द करें',
        mr: 'रद्द करा'
    },
    save: {
        en: 'Save',
        hi: 'सहेजें',
        mr: 'जतन करा'
    },
    delete: {
        en: 'Delete',
        hi: 'हटाएं',
        mr: 'हटवा'
    },
    edit: {
        en: 'Edit',
        hi: 'संपादित करें',
        mr: 'संपादित करा'
    },
    add: {
        en: 'Add',
        hi: 'जोड़ें',
        mr: 'जोडा'
    },
    search: {
        en: 'Search',
        hi: 'खोजें',
        mr: 'शोधा'
    },
    loading: {
        en: 'Loading...',
        hi: 'लोड हो रहा है...',
        mr: 'लोड होत आहे...'
    },
    error: {
        en: 'Error',
        hi: 'त्रुटि',
        mr: 'त्रुटी'
    },
    success: {
        en: 'Success',
        hi: 'सफलता',
        mr: 'यश'
    },

    // Plant Analysis
    plant_analysis: {
        en: 'Plant Analysis',
        hi: 'पौधे का विश्लेषण',
        mr: 'वनस्पती विश्लेषण'
    },
    health_score: {
        en: 'Health Score',
        hi: 'स्वास्थ्य स्कोर',
        mr: 'आरोग्य स्कोर'
    },
    disease_detected: {
        en: 'Disease Detected',
        hi: 'रोग पाया गया',
        mr: 'रोग आढळला'
    },
    no_disease: {
        en: 'No Disease Detected',
        hi: 'कोई रोग नहीं पाया गया',
        mr: 'कोणताही रोग आढळला नाही'
    },
    healthy: {
        en: 'Healthy',
        hi: 'स्वस्थ',
        mr: 'निरोगी'
    },
    severity: {
        en: 'Severity',
        hi: 'गंभीरता',
        mr: 'तीव्रता'
    },
    mild: {
        en: 'Mild',
        hi: 'हल्का',
        mr: 'सौम्य'
    },
    moderate: {
        en: 'Moderate',
        hi: 'मध्यम',
        mr: 'मध्यम'
    },
    severe: {
        en: 'Severe',
        hi: 'गंभीर',
        mr: 'गंभीर'
    },
    confidence: {
        en: 'Confidence',
        hi: 'विश्वास',
        mr: 'आत्मविश्वास'
    },
    plant_type: {
        en: 'Plant Type',
        hi: 'पौधे का प्रकार',
        mr: 'वनस्पती प्रकार'
    },
    care_plan: {
        en: 'Care Plan',
        hi: 'देखभाल योजना',
        mr: 'काळजी योजना'
    },
    recommendations: {
        en: 'Recommendations',
        hi: 'सिफारिशें',
        mr: 'शिफारसी'
    },
    treatment: {
        en: 'Treatment',
        hi: 'उपचार',
        mr: 'उपचार'
    },
    prevention: {
        en: 'Prevention',
        hi: 'रोकथाम',
        mr: 'प्रतिबंध'
    },
    download_report: {
        en: 'Download Report',
        hi: 'रिपोर्ट डाउनलोड करें',
        mr: 'अहवाल डाउनलोड करा'
    },
    download_pdf: {
        en: 'Download PDF',
        hi: 'PDF डाउनलोड करें',
        mr: 'PDF डाउनलोड करा'
    },
    download_image: {
        en: 'Save as Image',
        hi: 'छवि के रूप में सहेजें',
        mr: 'प्रतिमा म्हणून जतन करा'
    },

    // Plant Care
    watering: {
        en: 'Watering',
        hi: 'पानी देना',
        mr: 'पाणी देणे'
    },
    fertilizing: {
        en: 'Fertilizing',
        hi: 'खाद देना',
        mr: 'खत देणे'
    },
    sunlight: {
        en: 'Sunlight',
        hi: 'धूप',
        mr: 'सूर्यप्रकाश'
    },
    temperature: {
        en: 'Temperature',
        hi: 'तापमान',
        mr: 'तापमान'
    },
    humidity: {
        en: 'Humidity',
        hi: 'आर्द्रता',
        mr: 'आर्द्रता'
    },
    soil: {
        en: 'Soil',
        hi: 'मिट्टी',
        mr: 'माती'
    },
    pruning: {
        en: 'Pruning',
        hi: 'छंटाई',
        mr: 'छाटणी'
    },
    repotting: {
        en: 'Repotting',
        hi: 'पुनः गमले में लगाना',
        mr: 'पुनः कुंडीत लावणे'
    },

    // Reminders & Notifications
    reminder: {
        en: 'Reminder',
        hi: 'अनुस्मारक',
        mr: 'स्मरणपत्र'
    },
    water_reminder: {
        en: 'Time to water your plant!',
        hi: 'अपने पौधे को पानी देने का समय!',
        mr: 'तुमच्या रोपाला पाणी देण्याची वेळ!'
    },
    fertilize_reminder: {
        en: 'Time to fertilize your plant!',
        hi: 'अपने पौधे को खाद देने का समय!',
        mr: 'तुमच्या रोपाला खत देण्याची वेळ!'
    },
    set_reminder: {
        en: 'Set Reminder',
        hi: 'अनुस्मारक सेट करें',
        mr: 'स्मरणपत्र सेट करा'
    },
    reminder_frequency: {
        en: 'Reminder Frequency',
        hi: 'अनुस्मारक आवृत्ति',
        mr: 'स्मरणपत्र वारंवारता'
    },
    every_day: {
        en: 'Every day',
        hi: 'हर दिन',
        mr: 'दररोज'
    },
    every_week: {
        en: 'Every week',
        hi: 'हर सप्ताह',
        mr: 'दर आठवड्याला'
    },
    every_month: {
        en: 'Every month',
        hi: 'हर महीने',
        mr: 'दर महिन्याला'
    },
    no_notifications: {
        en: 'No notifications',
        hi: 'कोई सूचना नहीं',
        mr: 'कोणतीही सूचना नाही'
    },
    mark_as_read: {
        en: 'Mark as read',
        hi: 'पढ़ा हुआ चिह्नित करें',
        mr: 'वाचलेले म्हणून चिन्हांकित करा'
    },

    // Dashboard
    recent_analyses: {
        en: 'Recent Analyses',
        hi: 'हाल के विश्लेषण',
        mr: 'अलीकडील विश्लेषणे'
    },
    upcoming_reminders: {
        en: 'Upcoming Reminders',
        hi: 'आगामी अनुस्मारक',
        mr: 'आगामी स्मरणपत्रे'
    },
    total_plants: {
        en: 'Total Plants',
        hi: 'कुल पौधे',
        mr: 'एकूण रोपे'
    },
    analyses_this_month: {
        en: 'Analyses This Month',
        hi: 'इस महीने के विश्लेषण',
        mr: 'या महिन्यातील विश्लेषणे'
    },
    quick_actions: {
        en: 'Quick Actions',
        hi: 'त्वरित क्रियाएं',
        mr: 'जलद क्रिया'
    },
    analyze_plant: {
        en: 'Analyze Plant',
        hi: 'पौधे का विश्लेषण करें',
        mr: 'वनस्पती विश्लेषण करा'
    },
    add_plant: {
        en: 'Add Plant',
        hi: 'पौधा जोड़ें',
        mr: 'रोप जोडा'
    },
    view_history: {
        en: 'View History',
        hi: 'इतिहास देखें',
        mr: 'इतिहास पहा'
    },

    // Chatbot
    chat_title: {
        en: 'Yuki - Plant Assistant',
        hi: 'युकी - पौधा सहायक',
        mr: 'युकी - वनस्पती सहाय्यक'
    },
    chat_assistant: {
        en: 'Yuki',
        hi: 'युकी',
        mr: 'युकी'
    },
    chat_placeholder: {
        en: 'Ask Yuki anything about plant care...',
        hi: 'युकी से पौधों की देखभाल के बारे में कुछ भी पूछें...',
        mr: 'युकीला वनस्पती काळजीबद्दल काहीही विचारा...'
    },
    chat_welcome: {
        en: "Hello! I'm Yuki, your plant care assistant. How can I help you today?",
        hi: 'नमस्ते! मैं युकी हूं, आपका पौधा देखभाल सहायक। आज मैं आपकी कैसे मदद कर सकता हूं?',
        mr: 'नमस्कार! मी युकी आहे, तुमचा वनस्पती काळजी सहाय्यक. आज मी तुम्हाला कशी मदत करू शकतो?'
    },
    typing: {
        en: 'Typing...',
        hi: 'टाइप कर रहा है...',
        mr: 'टाइप करत आहे...'
    },
    send: {
        en: 'Send',
        hi: 'भेजें',
        mr: 'पाठवा'
    },
    clear_chat: {
        en: 'Clear Chat',
        hi: 'चैट साफ़ करें',
        mr: 'चॅट साफ करा'
    },

    // Forms & Inputs
    email: {
        en: 'Email',
        hi: 'ईमेल',
        mr: 'ईमेल'
    },
    password: {
        en: 'Password',
        hi: 'पासवर्ड',
        mr: 'पासवर्ड'
    },
    name: {
        en: 'Name',
        hi: 'नाम',
        mr: 'नाव'
    },
    plant_name: {
        en: 'Plant Name',
        hi: 'पौधे का नाम',
        mr: 'वनस्पतीचे नाव'
    },
    species: {
        en: 'Species',
        hi: 'प्रजाति',
        mr: 'प्रजाती'
    },
    location: {
        en: 'Location',
        hi: 'स्थान',
        mr: 'स्थान'
    },
    indoor: {
        en: 'Indoor',
        hi: 'घर के अंदर',
        mr: 'घरातील'
    },
    outdoor: {
        en: 'Outdoor',
        hi: 'बाहर',
        mr: 'बाहेरील'
    },
    garden: {
        en: 'Garden',
        hi: 'बगीचा',
        mr: 'बाग'
    },
    balcony: {
        en: 'Balcony',
        hi: 'बालकनी',
        mr: 'बाल्कनी'
    },
    notes: {
        en: 'Notes',
        hi: 'नोट्स',
        mr: 'नोट्स'
    },
    select_language: {
        en: 'Select Language',
        hi: 'भाषा चुनें',
        mr: 'भाषा निवडा'
    },
    english: {
        en: 'English',
        hi: 'अंग्रेज़ी',
        mr: 'इंग्रजी'
    },
    hindi: {
        en: 'Hindi',
        hi: 'हिंदी',
        mr: 'हिंदी'
    },
    marathi: {
        en: 'Marathi',
        hi: 'मराठी',
        mr: 'मराठी'
    },

    // Messages
    login_success: {
        en: 'Login successful',
        hi: 'लॉगिन सफल',
        mr: 'लॉगिन यशस्वी'
    },
    login_failed: {
        en: 'Login failed',
        hi: 'लॉगिन विफल',
        mr: 'लॉगिन अयशस्वी'
    },
    register_success: {
        en: 'Registration successful',
        hi: 'पंजीकरण सफल',
        mr: 'नोंदणी यशस्वी'
    },
    register_failed: {
        en: 'Registration failed',
        hi: 'पंजीकरण विफल',
        mr: 'नोंदणी अयशस्वी'
    },
    analysis_complete: {
        en: 'Analysis complete',
        hi: 'विश्लेषण पूर्ण',
        mr: 'विश्लेषण पूर्ण'
    },
    analysis_failed: {
        en: 'Analysis failed',
        hi: 'विश्लेषण विफल',
        mr: 'विश्लेषण अयशस्वी'
    },
    plant_added: {
        en: 'Plant added successfully',
        hi: 'पौधा सफलतापूर्वक जोड़ा गया',
        mr: 'रोप यशस्वीरित्या जोडले'
    },
    plant_updated: {
        en: 'Plant updated successfully',
        hi: 'पौधा सफलतापूर्वक अपडेट किया गया',
        mr: 'रोप यशस्वीरित्या अद्यतनित केले'
    },
    plant_deleted: {
        en: 'Plant deleted successfully',
        hi: 'पौधा सफलतापूर्वक हटाया गया',
        mr: 'रोप यशस्वीरित्या हटवले'
    },
    reminder_set: {
        en: 'Reminder set successfully',
        hi: 'अनुस्मारक सफलतापूर्वक सेट किया गया',
        mr: 'स्मरणपत्र यशस्वीरित्या सेट केले'
    },
    no_image_selected: {
        en: 'Please select an image',
        hi: 'कृपया एक छवि चुनें',
        mr: 'कृपया एक प्रतिमा निवडा'
    },
    invalid_file_type: {
        en: 'Invalid file type. Please upload an image.',
        hi: 'अमान्य फ़ाइल प्रकार। कृपया एक छवि अपलोड करें।',
        mr: 'अवैध फाइल प्रकार. कृपया एक प्रतिमा अपलोड करा.'
    },
    confirm_delete: {
        en: 'Are you sure you want to delete this?',
        hi: 'क्या आप वाकई इसे हटाना चाहते हैं?',
        mr: 'तुम्हाला खात्री आहे की तुम्ही हे हटवू इच्छिता?'
    },
    session_expired: {
        en: 'Session expired. Please login again.',
        hi: 'सत्र समाप्त। कृपया फिर से लॉगिन करें।',
        mr: 'सत्र संपले. कृपया पुन्हा लॉगिन करा.'
    },
    network_error: {
        en: 'Network error. Please check your connection.',
        hi: 'नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।',
        mr: 'नेटवर्क त्रुटी. कृपया तुमचे कनेक्शन तपासा.'
    },
    guest_continue: {
        en: 'Continue as Guest',
        hi: 'अतिथि के रूप में जारी रखें',
        mr: 'अतिथी म्हणून सुरू ठेवा'
    },
    or: {
        en: 'or',
        hi: 'या',
        mr: 'किंवा'
    },
    already_have_account: {
        en: 'Already have an account?',
        hi: 'पहले से ही खाता है?',
        mr: 'आधीच खाते आहे?'
    },
    dont_have_account: {
        en: "Don't have an account?",
        hi: 'खाता नहीं है?',
        mr: 'खाते नाही?'
    },
    drag_drop_image: {
        en: 'Drag and drop image here or click to upload',
        hi: 'छवि यहां खींचें और छोड़ें या अपलोड करने के लिए क्लिक करें',
        mr: 'येथे प्रतिमा ड्रॅग आणि ड्रॉप करा किंवा अपलोड करण्यासाठी क्लिक करा'
    },
    analyzing: {
        en: 'Analyzing your plant...',
        hi: 'आपके पौधे का विश्लेषण हो रहा है...',
        mr: 'तुमच्या रोपाचे विश्लेषण होत आहे...'
    },
    // Additional translations for new features
    welcome_message: {
        en: 'Welcome back',
        hi: 'फिर से स्वागत है',
        mr: 'पुन्हा स्वागत आहे'
    },
    dashboard_subtitle: {
        en: "Here's your plant health overview",
        hi: 'आपके पौधों के स्वास्थ्य का अवलोकन',
        mr: 'तुमच्या वनस्पतींच्या आरोग्याचा आढावा'
    },
    total_plants: {
        en: 'Total Plants',
        hi: 'कुल पौधे',
        mr: 'एकूण रोपे'
    },
    total_analyses: {
        en: 'Analyses',
        hi: 'विश्लेषण',
        mr: 'विश्लेषण'
    },
    pending_reminders: {
        en: 'Pending Reminders',
        hi: 'लंबित अनुस्मारक',
        mr: 'प्रलंबित स्मरणपत्रे'
    },
    avg_health: {
        en: 'Avg Health Score',
        hi: 'औसत स्वास्थ्य स्कोर',
        mr: 'सरासरी आरोग्य गुण'
    },
    quick_actions: {
        en: 'Quick Actions',
        hi: 'त्वरित कार्य',
        mr: 'जलद क्रिया'
    },
    analyze_plant: {
        en: 'Analyze Plant',
        hi: 'पौधे का विश्लेषण करें',
        mr: 'रोपाचे विश्लेषण करा'
    },
    add_plant: {
        en: 'Add Plant',
        hi: 'पौधा जोड़ें',
        mr: 'रोप जोडा'
    },
    view_history: {
        en: 'View History',
        hi: 'इतिहास देखें',
        mr: 'इतिहास पहा'
    },
    ask_assistant: {
        en: 'Ask Assistant',
        hi: 'सहायक से पूछें',
        mr: 'सहाय्यकाला विचारा'
    },
    recent_analyses: {
        en: 'Recent Analyses',
        hi: 'हाल के विश्लेषण',
        mr: 'अलीकडील विश्लेषण'
    },
    upcoming_reminders: {
        en: 'Upcoming Reminders',
        hi: 'आगामी अनुस्मारक',
        mr: 'आगामी स्मरणपत्रे'
    },
    no_analyses_yet: {
        en: 'No analyses yet. Start by analyzing a plant!',
        hi: 'अभी तक कोई विश्लेषण नहीं। पौधे का विश्लेषण करके शुरू करें!',
        mr: 'अजून विश्लेषण नाही. रोपाचे विश्लेषण करून सुरुवात करा!'
    },
    analyze_now: {
        en: 'Analyze Now',
        hi: 'अभी विश्लेषण करें',
        mr: 'आता विश्लेषण करा'
    },
    no_reminders: {
        en: 'No upcoming reminders',
        hi: 'कोई आगामी अनुस्मारक नहीं',
        mr: 'आगामी स्मरणपत्रे नाहीत'
    },
    no_plants: {
        en: 'No plants added yet',
        hi: 'अभी तक कोई पौधा नहीं जोड़ा गया',
        mr: 'अजून रोपे जोडले नाहीत'
    },
    add_first_plant: {
        en: 'Add Your First Plant',
        hi: 'अपना पहला पौधा जोड़ें',
        mr: 'तुमचे पहिले रोप जोडा'
    },
    plant_assistant: {
        en: 'Plant Assistant',
        hi: 'पौधा सहायक',
        mr: 'वनस्पती सहाय्यक'
    },
    ask_anything: {
        en: 'Ask me anything about plants!',
        hi: 'पौधों के बारे में कुछ भी पूछें!',
        mr: 'वनस्पतींबद्दल काहीही विचारा!'
    },
    chat_greeting: {
        en: "Hello! I'm your plant care assistant. How can I help you today?",
        hi: 'नमस्ते! मैं आपका पौधों की देखभाल सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?',
        mr: 'नमस्कार! मी तुमचा वनस्पती काळजी सहाय्यक आहे. आज मी तुमची कशी मदत करू शकतो?'
    },
    type_question: {
        en: 'Type your question...',
        hi: 'अपना प्रश्न लिखें...',
        mr: 'तुमचा प्रश्न लिहा...'
    },
    no_notifications: {
        en: 'No notifications',
        hi: 'कोई सूचना नहीं',
        mr: 'सूचना नाहीत'
    },
    mark_all_read: {
        en: 'Mark all as read',
        hi: 'सभी को पढ़ा हुआ चिह्नित करें',
        mr: 'सर्व वाचलेले म्हणून चिन्हांकित करा'
    },
    profile: {
        en: 'Profile',
        hi: 'प्रोफ़ाइल',
        mr: 'प्रोफाइल'
    },
    view_all: {
        en: 'View All',
        hi: 'सभी देखें',
        mr: 'सर्व पहा'
    },
    manage: {
        en: 'Manage',
        hi: 'प्रबंधित करें',
        mr: 'व्यवस्थापित करा'
    },
    today: {
        en: 'Today',
        hi: 'आज',
        mr: 'आज'
    },
    tomorrow: {
        en: 'Tomorrow',
        hi: 'कल',
        mr: 'उद्या'
    },
    just_now: {
        en: 'Just now',
        hi: 'अभी',
        mr: 'आत्ताच'
    },
    plant: {
        en: 'Plant',
        hi: 'पौधा',
        mr: 'रोप'
    },
    health: {
        en: 'Health',
        hi: 'स्वास्थ्य',
        mr: 'आरोग्य'
    },
    date: {
        en: 'Date',
        hi: 'तारीख',
        mr: 'तारीख'
    },
    error_occurred: {
        en: 'An error occurred. Please try again.',
        hi: 'एक त्रुटि हुई। कृपया पुनः प्रयास करें।',
        mr: 'एक त्रुटी आली. कृपया पुन्हा प्रयत्न करा.'
    },
    nav_dashboard: {
        en: 'Dashboard',
        hi: 'डैशबोर्ड',
        mr: 'डॅशबोर्ड'
    },
    nav_analyze: {
        en: 'Analyze Plant',
        hi: 'पौधे का विश्लेषण',
        mr: 'रोप विश्लेषण'
    },
    nav_my_plants: {
        en: 'My Plants',
        hi: 'मेरे पौधे',
        mr: 'माझी रोपे'
    },
    nav_history: {
        en: 'History',
        hi: 'इतिहास',
        mr: 'इतिहास'
    },
    // Login/Register
    login_success: {
        en: 'Login successful!',
        hi: 'लॉगिन सफल!',
        mr: 'लॉगिन यशस्वी!'
    },
    redirecting: {
        en: 'Redirecting...',
        hi: 'रीडायरेक्ट हो रहा है...',
        mr: 'पुनर्निर्देशित होत आहे...'
    },
    enter_email_password: {
        en: 'Please enter email and password',
        hi: 'कृपया ईमेल और पासवर्ड दर्ज करें',
        mr: 'कृपया ईमेल आणि पासवर्ड प्रविष्ट करा'
    },
    login_failed: {
        en: 'Login failed. Please try again.',
        hi: 'लॉगिन विफल। कृपया पुनः प्रयास करें।',
        mr: 'लॉगिन अयशस्वी. कृपया पुन्हा प्रयत्न करा.'
    },
    guest_login_failed: {
        en: 'Guest login failed',
        hi: 'अतिथि लॉगिन विफल',
        mr: 'अतिथी लॉगिन अयशस्वी'
    },
    connection_error: {
        en: 'Connection error. Please check if the server is running.',
        hi: 'कनेक्शन त्रुटि। कृपया जांचें कि सर्वर चल रहा है।',
        mr: 'कनेक्शन त्रुटी. कृपया सर्व्हर चालू आहे का ते तपासा.'
    },
    demo_credentials_filled: {
        en: 'Demo credentials filled. Click Login to continue.',
        hi: 'डेमो क्रेडेंशियल भरे गए। जारी रखने के लिए लॉगिन पर क्लिक करें।',
        mr: 'डेमो क्रेडेंशियल्स भरले. सुरू ठेवण्यासाठी लॉगिन वर क्लिक करा.'
    },
    no_account: {
        en: "Don't have an account?",
        hi: 'खाता नहीं है?',
        mr: 'खाते नाही?'
    },
    have_account: {
        en: 'Already have an account?',
        hi: 'पहले से खाता है?',
        mr: 'आधीच खाते आहे?'
    },
    enter_name: {
        en: 'Please enter your name',
        hi: 'कृपया अपना नाम दर्ज करें',
        mr: 'कृपया तुमचे नाव प्रविष्ट करा'
    },
    passwords_not_match: {
        en: 'Passwords do not match',
        hi: 'पासवर्ड मेल नहीं खाते',
        mr: 'पासवर्ड जुळत नाहीत'
    },
    password_min_length: {
        en: 'Password must be at least 6 characters',
        hi: 'पासवर्ड कम से कम 6 वर्ण का होना चाहिए',
        mr: 'पासवर्ड किमान 6 वर्णांचा असावा'
    },
    registration_failed: {
        en: 'Registration failed. Please try again.',
        hi: 'पंजीकरण विफल। कृपया पुनः प्रयास करें।',
        mr: 'नोंदणी अयशस्वी. कृपया पुन्हा प्रयत्न करा.'
    },
    email: {
        en: 'Email Address',
        hi: 'ईमेल पता',
        mr: 'ईमेल पत्ता'
    },
    password: {
        en: 'Password',
        hi: 'पासवर्ड',
        mr: 'पासवर्ड'
    },
    confirm_password: {
        en: 'Confirm Password',
        hi: 'पासवर्ड की पुष्टि करें',
        mr: 'पासवर्ड पुष्टी करा'
    },
    name: {
        en: 'Full Name',
        hi: 'पूरा नाम',
        mr: 'पूर्ण नाव'
    },
    // Plants page
    manage_plants_desc: {
        en: 'Manage your plants and set care reminders',
        hi: 'अपने पौधों को प्रबंधित करें और देखभाल अनुस्मारक सेट करें',
        mr: 'तुमची रोपे व्यवस्थापित करा आणि काळजी स्मरणपत्रे सेट करा'
    },
    plants: {
        en: 'Plants',
        hi: 'पौधे',
        mr: 'रोपे'
    },
    reminders: {
        en: 'Reminders',
        hi: 'अनुस्मारक',
        mr: 'स्मरणपत्रे'
    },
    add_new_plant: {
        en: 'Add New Plant',
        hi: 'नया पौधा जोड़ें',
        mr: 'नवीन रोप जोडा'
    },
    plant_name: {
        en: 'Plant Name',
        hi: 'पौधे का नाम',
        mr: 'रोपाचे नाव'
    },
    species: {
        en: 'Species',
        hi: 'प्रजाति',
        mr: 'प्रजाती'
    },
    location: {
        en: 'Location',
        hi: 'स्थान',
        mr: 'स्थान'
    },
    indoor: {
        en: 'Indoor',
        hi: 'घर के अंदर',
        mr: 'घरात'
    },
    outdoor: {
        en: 'Outdoor',
        hi: 'बाहर',
        mr: 'बाहेर'
    },
    balcony: {
        en: 'Balcony',
        hi: 'बालकनी',
        mr: 'बाल्कनी'
    },
    garden: {
        en: 'Garden',
        hi: 'बगीचा',
        mr: 'बाग'
    },
    plant_image: {
        en: 'Plant Image',
        hi: 'पौधे की छवि',
        mr: 'रोपाची प्रतिमा'
    },
    notes: {
        en: 'Notes',
        hi: 'नोट्स',
        mr: 'नोट्स'
    },
    set_reminders: {
        en: 'Set Reminders',
        hi: 'अनुस्मारक सेट करें',
        mr: 'स्मरणपत्रे सेट करा'
    },
    watering: {
        en: 'Watering',
        hi: 'पानी देना',
        mr: 'पाणी देणे'
    },
    fertilizing: {
        en: 'Fertilizing',
        hi: 'खाद देना',
        mr: 'खत देणे'
    },
    edit_plant: {
        en: 'Edit Plant',
        hi: 'पौधा संपादित करें',
        mr: 'रोप संपादित करा'
    },
    save_changes: {
        en: 'Save Changes',
        hi: 'परिवर्तन सहेजें',
        mr: 'बदल जतन करा'
    },
    confirm_delete_plant: {
        en: 'Are you sure you want to delete this plant?',
        hi: 'क्या आप वाकई इस पौधे को हटाना चाहते हैं?',
        mr: 'तुम्हाला खात्री आहे की हे रोप हटवायचे आहे?'
    },
    all_reminders: {
        en: 'All Reminders',
        hi: 'सभी अनुस्मारक',
        mr: 'सर्व स्मरणपत्रे'
    },
    add_reminder: {
        en: 'Add Reminder',
        hi: 'अनुस्मारक जोड़ें',
        mr: 'स्मरणपत्र जोडा'
    },
    no_reminders_set: {
        en: 'No reminders set',
        hi: 'कोई अनुस्मारक सेट नहीं',
        mr: 'स्मरणपत्रे सेट नाहीत'
    },
    upcoming_this_week: {
        en: 'Upcoming This Week',
        hi: 'इस सप्ताह आने वाले',
        mr: 'या आठवड्यात येणारे'
    },
    all_caught_up: {
        en: 'All caught up!',
        hi: 'सब अपडेट है!',
        mr: 'सर्व पूर्ण!'
    },
    reminder_type: {
        en: 'Reminder Type',
        hi: 'अनुस्मारक प्रकार',
        mr: 'स्मरणपत्र प्रकार'
    },
    custom_title: {
        en: 'Custom Title',
        hi: 'कस्टम शीर्षक',
        mr: 'सानुकूल शीर्षक'
    },
    select_plant: {
        en: 'Select Plant',
        hi: 'पौधा चुनें',
        mr: 'रोप निवडा'
    },
    frequency_days: {
        en: 'Frequency (Days)',
        hi: 'आवृत्ति (दिन)',
        mr: 'वारंवारता (दिवस)'
    },
    confirm_delete_reminder: {
        en: 'Are you sure you want to delete this reminder?',
        hi: 'क्या आप वाकई इस अनुस्मारक को हटाना चाहते हैं?',
        mr: 'तुम्हाला खात्री आहे की हे स्मरणपत्र हटवायचे आहे?'
    },
    plant_name_required: {
        en: 'Plant name is required',
        hi: 'पौधे का नाम आवश्यक है',
        mr: 'रोपाचे नाव आवश्यक आहे'
    },
    // History page
    analysis_history: {
        en: 'Analysis History',
        hi: 'विश्लेषण इतिहास',
        mr: 'विश्लेषण इतिहास'
    },
    history_subtitle: {
        en: 'View your past plant health analyses and reports',
        hi: 'अपने पिछले पौधे स्वास्थ्य विश्लेषण और रिपोर्ट देखें',
        mr: 'तुमचे मागील वनस्पती आरोग्य विश्लेषण आणि अहवाल पहा'
    },
    search: {
        en: 'Search...',
        hi: 'खोजें...',
        mr: 'शोधा...'
    },
    all_health: {
        en: 'All',
        hi: 'सभी',
        mr: 'सर्व'
    },
    healthy: {
        en: 'Healthy',
        hi: 'स्वस्थ',
        mr: 'निरोगी'
    },
    moderate: {
        en: 'Moderate',
        hi: 'मध्यम',
        mr: 'मध्यम'
    },
    unhealthy: {
        en: 'Unhealthy',
        hi: 'अस्वस्थ',
        mr: 'अस्वस्थ'
    },
    loading: {
        en: 'Loading...',
        hi: 'लोड हो रहा है...',
        mr: 'लोड होत आहे...'
    },
    no_history: {
        en: 'No analysis history',
        hi: 'कोई विश्लेषण इतिहास नहीं',
        mr: 'विश्लेषण इतिहास नाही'
    },
    no_history_desc: {
        en: 'Start by analyzing a plant to see your history',
        hi: 'अपना इतिहास देखने के लिए पौधे का विश्लेषण करके शुरू करें',
        mr: 'तुमचा इतिहास पाहण्यासाठी रोपाचे विश्लेषण करा'
    },
    analyze_first: {
        en: 'Analyze Your First Plant',
        hi: 'अपने पहले पौधे का विश्लेषण करें',
        mr: 'तुमच्या पहिल्या रोपाचे विश्लेषण करा'
    },
    select_analysis: {
        en: 'Select an analysis to view details',
        hi: 'विवरण देखने के लिए एक विश्लेषण चुनें',
        mr: 'तपशील पाहण्यासाठी विश्लेषण निवडा'
    },
    select_analysis_desc: {
        en: 'Click on any analysis from the list to see full details',
        hi: 'पूर्ण विवरण देखने के लिए सूची से किसी भी विश्लेषण पर क्लिक करें',
        mr: 'पूर्ण तपशील पाहण्यासाठी सूचीमधील कोणत्याही विश्लेषणावर क्लिक करा'
    },
    unknown_plant: {
        en: 'Unknown Plant',
        hi: 'अज्ञात पौधा',
        mr: 'अज्ञात रोप'
    },
    summary: {
        en: 'Summary',
        hi: 'सारांश',
        mr: 'सारांश'
    },
    detected_issues: {
        en: 'Detected Issues',
        hi: 'पहचानी गई समस्याएं',
        mr: 'आढळलेले मुद्दे'
    },
    recommendations: {
        en: 'Recommendations',
        hi: 'सिफारिशें',
        mr: 'शिफारसी'
    },
    care_tips: {
        en: 'Care Tips',
        hi: 'देखभाल टिप्स',
        mr: 'काळजी टिप्स'
    },
    download_pdf: {
        en: 'Download PDF',
        hi: 'PDF डाउनलोड करें',
        mr: 'PDF डाउनलोड करा'
    },
    download_image: {
        en: 'Download Image',
        hi: 'छवि डाउनलोड करें',
        mr: 'प्रतिमा डाउनलोड करा'
    },
    download_failed: {
        en: 'Download failed. Please try again.',
        hi: 'डाउनलोड विफल। कृपया पुनः प्रयास करें।',
        mr: 'डाउनलोड अयशस्वी. कृपया पुन्हा प्रयत्न करा.'
    },
    confirm_delete_analysis: {
        en: 'Are you sure you want to delete this analysis?',
        hi: 'क्या आप वाकई इस विश्लेषण को हटाना चाहते हैं?',
        mr: 'तुम्हाला खात्री आहे की हे विश्लेषण हटवायचे आहे?'
    },

    // Index page translations
    hero_subtitle: {
        en: 'Upload a photo of your plant and get instant AI-powered disease detection and care recommendations',
        hi: 'अपने पौधे की एक फोटो अपलोड करें और तुरंत AI-संचालित रोग का पता लगाएं और देखभाल की सिफारिशें प्राप्त करें',
        mr: 'तुमच्या रोपाचा फोटो अपलोड करा आणि AI-संचालित रोग ओळख आणि काळजी शिफारसी त्वरित मिळवा'
    },
    upload_plant_image: {
        en: 'Upload Plant Image',
        hi: 'पौधे की छवि अपलोड करें',
        mr: 'रोपाची प्रतिमा अपलोड करा'
    },
    choose_file: {
        en: 'Choose File',
        hi: 'फ़ाइल चुनें',
        mr: 'फाइल निवडा'
    },
    clear: {
        en: 'Clear',
        hi: 'साफ़ करें',
        mr: 'साफ करा'
    },
    confidence_threshold: {
        en: 'Confidence Threshold',
        hi: 'विश्वास सीमा',
        mr: 'विश्वास मर्यादा'
    },
    confidence_hint: {
        en: 'Higher values = more confident predictions',
        hi: 'उच्च मान = अधिक आत्मविश्वासपूर्ण भविष्यवाणियां',
        mr: 'उच्च मूल्ये = अधिक आत्मविश्वासपूर्ण अंदाज'
    },
    ai_analyzing: {
        en: '🔬 AI is analyzing your plant...',
        hi: '🔬 AI आपके पौधे का विश्लेषण कर रहा है...',
        mr: '🔬 AI तुमच्या रोपाचे विश्लेषण करत आहे...'
    },
    please_wait: {
        en: 'This may take a few seconds',
        hi: 'इसमें कुछ सेकंड लग सकते हैं',
        mr: 'यास काही सेकंद लागू शकतात'
    },
    plant_identified: {
        en: 'Plant Identified',
        hi: 'पौधे की पहचान हुई',
        mr: 'रोप ओळखले'
    },
    family: {
        en: 'Family',
        hi: 'परिवार',
        mr: 'कुटुंब'
    },
    type: {
        en: 'Type',
        hi: 'प्रकार',
        mr: 'प्रकार'
    },
    origin: {
        en: 'Origin',
        hi: 'मूल स्थान',
        mr: 'मूळ ठिकाण'
    },
    ideal_conditions: {
        en: 'Ideal Conditions',
        hi: 'आदर्श परिस्थितियां',
        mr: 'आदर्श परिस्थिती'
    },
    general_care: {
        en: 'General Care',
        hi: 'सामान्य देखभाल',
        mr: 'सामान्य काळजी'
    },
    common_issues: {
        en: 'Common Issues',
        hi: 'सामान्य समस्याएं',
        mr: 'सामान्य समस्या'
    },
    disease_analysis: {
        en: 'Disease Analysis',
        hi: 'रोग विश्लेषण',
        mr: 'रोग विश्लेषण'
    },
    symptoms_observed: {
        en: 'Symptoms Observed',
        hi: 'देखे गए लक्षण',
        mr: 'निरीक्षण केलेली लक्षणे'
    },
    probable_causes: {
        en: 'Probable Causes',
        hi: 'संभावित कारण',
        mr: 'संभाव्य कारणे'
    },
    ai_confidence: {
        en: 'AI Confidence',
        hi: 'AI विश्वास',
        mr: 'AI विश्वास'
    },
    risk_if_untreated: {
        en: 'Risk if Untreated',
        hi: 'उपचार न करने पर जोखिम',
        mr: 'उपचार न केल्यास धोका'
    },
    treatment_care_plan: {
        en: 'Treatment & Care Plan',
        hi: 'उपचार और देखभाल योजना',
        mr: 'उपचार आणि काळजी योजना'
    },
    immediate_actions: {
        en: 'Immediate Actions',
        hi: 'तत्काल कार्रवाई',
        mr: 'तात्काळ कृती'
    },
    watering_guide: {
        en: 'Watering Guide',
        hi: 'पानी देने की गाइड',
        mr: 'पाणी देण्याची मार्गदर्शिका'
    },
    treatment_options: {
        en: 'Treatment Options',
        hi: 'उपचार विकल्प',
        mr: 'उपचार पर्याय'
    },
    organic: {
        en: 'Organic',
        hi: 'जैविक',
        mr: 'सेंद्रिय'
    },
    chemical: {
        en: 'Chemical',
        hi: 'रासायनिक',
        mr: 'रासायनिक'
    },
    cultural: {
        en: 'Cultural',
        hi: 'सांस्कृतिक',
        mr: 'सांस्कृतिक'
    },
    recovery_timeline: {
        en: 'Recovery Timeline',
        hi: 'पुनर्प्राप्ति समयरेखा',
        mr: 'पुनर्प्राप्ती कालावधी'
    },
    quick_tips: {
        en: 'Quick Tips',
        hi: 'त्वरित टिप्स',
        mr: 'जलद टिप्स'
    },
    detailed_analysis: {
        en: 'Detailed Analysis',
        hi: 'विस्तृत विश्लेषण',
        mr: 'तपशीलवार विश्लेषण'
    },
    feature_analysis: {
        en: 'Feature Analysis',
        hi: 'विशेषता विश्लेषण',
        mr: 'वैशिष्ट्य विश्लेषण'
    },
    roi_analysis: {
        en: 'ROI Analysis',
        hi: 'ROI विश्लेषण',
        mr: 'ROI विश्लेषण'
    }
};

// Current language
let currentLanguage = localStorage.getItem('language') || 'en';

/**
 * Get translated text
 * @param {string} key - Translation key
 * @param {string} lang - Language code (optional, uses currentLanguage)
 * @returns {string} - Translated text
 */
function t(key, lang = null) {
    const language = lang || currentLanguage;
    
    if (!TRANSLATIONS[key]) {
        console.warn(`Translation missing for key: ${key}`);
        return key;
    }
    
    return TRANSLATIONS[key][language] || TRANSLATIONS[key]['en'] || key;
}

/**
 * Set current language
 * @param {string} lang - Language code (en, hi, mr)
 */
function setLanguage(lang) {
    if (['en', 'hi', 'mr'].includes(lang)) {
        currentLanguage = lang;
        localStorage.setItem('language', lang);
        
        // Update user preference on server if logged in
        const token = localStorage.getItem('authToken');
        if (token) {
            fetch('/api/v1/auth/language', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ language: lang })
            }).catch(err => console.log('Failed to update language preference:', err));
        }
        
        // Trigger page update
        translatePage();
        
        // Dispatch event for components to react
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    }
}

/**
 * Get current language
 * @returns {string} - Current language code
 */
function getLanguage() {
    return currentLanguage;
}

/**
 * Get all supported languages
 * @returns {Array} - List of supported languages
 */
function getSupportedLanguages() {
    return [
        { code: 'en', name: 'English', native: 'English', flag: '🇬🇧' },
        { code: 'hi', name: 'Hindi', native: 'हिंदी', flag: '🇮🇳' },
        { code: 'mr', name: 'Marathi', native: 'मराठी', flag: '🇮🇳' }
    ];
}

/**
 * Translate all elements with data-i18n attribute
 */
function translatePage() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        // Handle different element types
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.placeholder) {
                element.placeholder = translation;
            }
        } else {
            element.textContent = translation;
        }
    });
    
    // Handle placeholders separately
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.placeholder = t(key);
    });
    
    // Handle title attributes
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.title = t(key);
    });
}

/**
 * Create language selector dropdown HTML
 * @param {string} currentLang - Currently selected language
 * @returns {string} - HTML string for language selector
 */
function createLanguageSelector(currentLang = null) {
    const lang = currentLang || currentLanguage;
    const languages = getSupportedLanguages();
    const current = languages.find(l => l.code === lang) || languages[0];
    
    return `
        <div class="dropdown language-selector">
            <button class="btn btn-outline-secondary dropdown-toggle" type="button" 
                    id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                <span class="me-1">${current.flag}</span>
                <span class="d-none d-md-inline">${current.native}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="languageDropdown">
                ${languages.map(l => `
                    <li>
                        <a class="dropdown-item ${l.code === lang ? 'active' : ''}" 
                           href="#" onclick="setLanguage('${l.code}'); return false;">
                            <span class="me-2">${l.flag}</span>
                            ${l.native} (${l.name})
                        </a>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Try to get language from user profile if logged in
    const userData = localStorage.getItem('userData');
    if (userData) {
        try {
            const user = JSON.parse(userData);
            if (user.language && ['en', 'hi', 'mr'].includes(user.language)) {
                currentLanguage = user.language;
                localStorage.setItem('language', user.language);
            }
        } catch (e) {
            // Ignore parse errors
        }
    }
    
    // Translate page
    translatePage();
});

// Export for use in other scripts
window.t = t;
window.setLanguage = setLanguage;
window.getLanguage = getLanguage;
window.getSupportedLanguages = getSupportedLanguages;
window.translatePage = translatePage;
window.createLanguageSelector = createLanguageSelector;
window.TRANSLATIONS = TRANSLATIONS;

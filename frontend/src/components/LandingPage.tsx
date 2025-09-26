import React, { useState, useEffect } from 'react';
import { ArrowRightIcon, HeartIcon, UserGroupIcon, ChatBubbleLeftRightIcon, 
         ShieldCheckIcon, GlobeAltIcon, ClockIcon, SparklesIcon, 
         PhoneIcon, MapPinIcon, UserIcon, StarIcon } from '@heroicons/react/24/outline';

interface LandingPageProps {
  onTryNowClick: () => void;
  isAuthenticated: boolean;
}

const LandingPage: React.FC<LandingPageProps> = ({ onTryNowClick, isAuthenticated }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentTip, setCurrentTip] = useState(0);
  const [stats, setStats] = useState({
    users: 0,
    consultations: 0,
    languages: 0
  });

  // Animation on component mount
  useEffect(() => {
    setIsVisible(true);
    
    // Animate statistics
    const animateStats = () => {
      const targetStats = { users: 15000, consultations: 50000, languages: 12 };
      const duration = 2000;
      const steps = 60;
      const stepDuration = duration / steps;
      
      let currentStep = 0;
      const timer = setInterval(() => {
        currentStep++;
        const progress = currentStep / steps;
        setStats({
          users: Math.floor(targetStats.users * progress),
          consultations: Math.floor(targetStats.consultations * progress),
          languages: Math.floor(targetStats.languages * progress)
        });
        
        if (currentStep >= steps) {
          clearInterval(timer);
        }
      }, stepDuration);
    };
    
    setTimeout(animateStats, 1000);
  }, []);

  // Health tips carousel
  const healthTips = [
    "💧 Drink at least 8 glasses of water daily for optimal health",
    "🏃‍♂️ 30 minutes of walking daily can reduce disease risk by 40%",
    "😴 Quality sleep for 7-8 hours is essential for immune function",
    "🥗 Eat colorful fruits and vegetables for maximum nutrition",
    "🧘‍♀️ Practice deep breathing to reduce stress and anxiety"
  ];

  useEffect(() => {
    const tipTimer = setInterval(() => {
      setCurrentTip((prev) => (prev + 1) % healthTips.length);
    }, 4000);
    
    return () => clearInterval(tipTimer);
  }, [healthTips.length]);

  // Add smooth scrolling behavior for navigation links
  useEffect(() => {
    // Add smooth scrolling to HTML element
    document.documentElement.style.scrollBehavior = 'smooth';
    
    return () => {
      // Clean up on component unmount
      document.documentElement.style.scrollBehavior = 'auto';
    };
  }, []);

  const testimonials = [
    {
      name: "प्रिया शर्मा",
      location: "उत्तर प्रदेश",
      text: "स्वास्थ्य मित्र ने मेरे बच्चे की सर्दी के बारे में सही सलाह दी। बहुत उपयोगी है।",
      rating: 5
    },
    {
      name: "রহিম উদ্দিন",
      location: "পশ্চিমবঙ্গ",
      text: "গ্রামাঞ্চলে এমন সেবা পাওয়া দুর্দান্ত। সহজ ভাষায় স্বাস্থ্য পরামর্শ পাই।",
      rating: 5
    },
    {
      name: "മേരി ജോസഫ്",
      location: "കേരളം",
      text: "അടിയന്തിര സാഹചര്യത്തിൽ ഈ ആപ്പ് വളരെ സഹായകമായിരുന്നു।",
      rating: 5
    }
  ];
  
  const handleTryNowClick = async () => {
    try {
      // Start the Flask app in the backend
      const response = await fetch('http://localhost:5000/', {
        method: 'HEAD'
      });
      // Redirect to the new sih folder's index.html
      window.location.href = '/sih_new/index.html';
    } catch (error) {
      // If Flask app is not running, redirect anyway
      console.log('Flask app might not be running, redirecting to new sih folder...');
      window.location.href = '/sih_new/index.html';
    }
  };

  const handleEmergencyClick = () => {
    // Open phone dialer with 108 pre-dialed
    window.location.href = 'tel:108';
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute top-1/2 -left-20 w-60 h-60 bg-indigo-200 rounded-full opacity-20 animate-bounce"></div>
        <div className="absolute bottom-20 right-1/4 w-40 h-40 bg-green-200 rounded-full opacity-20 animate-pulse"></div>
      </div>

      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className={`flex items-center transition-all duration-1000 ${isVisible ? 'translate-x-0 opacity-100' : '-translate-x-20 opacity-0'}`}>
              <div className="relative">
                <HeartIcon className="h-8 w-8 text-blue-600 mr-3 animate-pulse" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                WellBot
              </h1>
              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded-full font-semibold">
                AI-Powered
              </span>
            </div>
            <nav className={`hidden md:flex space-x-8 transition-all duration-1000 delay-300 ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0'}`}>
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-all duration-300 hover:scale-105 relative group">
                Features
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-300 group-hover:w-full"></span>
              </a>
              <a href="#stats" className="text-gray-600 hover:text-blue-600 transition-all duration-300 hover:scale-105 relative group">
                Impact
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-300 group-hover:w-full"></span>
              </a>
              <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-all duration-300 hover:scale-105 relative group">
                Stories
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-300 group-hover:w-full"></span>
              </a>
              <a href="#about" className="text-gray-600 hover:text-blue-600 transition-all duration-300 hover:scale-105 relative group">
                About
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-300 group-hover:w-full"></span>
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Health Tip Banner */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 px-4 relative overflow-hidden">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <SparklesIcon className="h-5 w-5 mr-2 animate-spin" />
          <div className="transition-all duration-500 ease-in-out">
            {healthTips[currentTip]}
          </div>
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"></div>
      </div>

      {/* Hero Section */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-20 text-center">
          <div className={`max-w-4xl mx-auto transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Healthcare Guidance for
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 block animate-gradient">
                Rural Communities
              </span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
              Get instant access to <span className="font-semibold text-blue-600">AI-powered health assistance</span> designed 
              specifically for rural areas. Ask questions, get guidance, and connect with healthcare resources when you need them most.
            </p>
            
            {/* Enhanced CTA Section */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
              <button
                onClick={handleTryNowClick}
                className="group inline-flex items-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-2xl relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2 group-hover:animate-bounce" />
                Start Chatting Now
                <ArrowRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
              </button>
              
              <button 
                onClick={handleEmergencyClick}
                className="inline-flex items-center px-6 py-3 text-blue-600 bg-blue-50 rounded-xl hover:bg-blue-100 transition-all duration-300 font-semibold border-2 border-transparent hover:border-blue-200"
              >
                <PhoneIcon className="h-5 w-5 mr-2" />
                Emergency: 108
              </button>
            </div>
            
            <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-ping"></div>
                Available 24/7
              </div>
              <div className="flex items-center">
                <GlobeAltIcon className="h-4 w-4 mr-1" />
                12 Languages
              </div>
              <div className="flex items-center">
                <ShieldCheckIcon className="h-4 w-4 mr-1" />
                100% Secure
              </div>
            </div>
          </div>
        </div>

        {/* Statistics Section */}
        <section id="stats" className="py-16 bg-gradient-to-r from-blue-600 to-indigo-600 text-white -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 relative overflow-hidden scroll-mt-24">
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="relative max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h3 className="text-3xl font-bold mb-4">Making a Real Impact</h3>
              <p className="text-blue-100 text-lg">Trusted by thousands across rural India</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="text-4xl font-bold mb-2">{stats.users.toLocaleString()}+</div>
                <div className="text-blue-100 text-lg font-semibold mb-1">Users Helped</div>
                <p className="text-blue-200 text-sm">Across rural communities</p>
              </div>
              
              <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="text-4xl font-bold mb-2">{stats.consultations.toLocaleString()}+</div>
                <div className="text-blue-100 text-lg font-semibold mb-1">Consultations</div>
                <p className="text-blue-200 text-sm">Health queries resolved</p>
              </div>
              
              <div className="text-center p-6 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="text-4xl font-bold mb-2">{stats.languages}+</div>
                <div className="text-blue-100 text-lg font-semibold mb-1">Languages</div>
                <p className="text-blue-200 text-sm">Breaking language barriers</p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">Why Choose WellBot?</h3>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Designed with rural communities in mind, our platform provides accessible, reliable, and culturally-sensitive healthcare guidance
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="group text-center p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 transition-all duration-300 transform hover:-translate-y-2 hover:shadow-xl border border-blue-100">
              <div className="relative">
                <ChatBubbleLeftRightIcon className="h-16 w-16 text-blue-600 mx-auto mb-6 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center">
                  <SparklesIcon className="h-3 w-3 text-white" />
                </div>
              </div>
              <h4 className="text-2xl font-bold text-gray-900 mb-4">AI-Powered Chat</h4>
              <p className="text-gray-600 leading-relaxed">
                Get instant, accurate responses to your health questions with our intelligent chatbot trained on vast medical knowledge and rural health data
              </p>
            </div>
            
            <div className="group text-center p-8 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 transition-all duration-300 transform hover:-translate-y-2 hover:shadow-xl border border-green-100">
              <div className="relative">
                <UserGroupIcon className="h-16 w-16 text-green-600 mx-auto mb-6 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-400 rounded-full flex items-center justify-center">
                  <HeartIcon className="h-3 w-3 text-white" />
                </div>
              </div>
              <h4 className="text-2xl font-bold text-gray-900 mb-4">Rural-Focused</h4>
              <p className="text-gray-600 leading-relaxed">
                Specifically designed for rural communities with limited healthcare access, understanding local contexts and cultural sensitivities
              </p>
            </div>
            
            <div className="group text-center p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 transition-all duration-300 transform hover:-translate-y-2 hover:shadow-xl border border-purple-100">
              <div className="relative">
                <ShieldCheckIcon className="h-16 w-16 text-purple-600 mx-auto mb-6 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-400 rounded-full flex items-center justify-center">
                  <ClockIcon className="h-3 w-3 text-white" />
                </div>
              </div>
              <h4 className="text-2xl font-bold text-gray-900 mb-4">Safe & Available 24/7</h4>
              <p className="text-gray-600 leading-relaxed">
                Your health information is protected with enterprise-grade security while being available round the clock for emergencies
              </p>
            </div>
          </div>

          {/* Additional Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow duration-300">
              <GlobeAltIcon className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <div className="font-semibold text-gray-900">Multilingual</div>
                <div className="text-sm text-gray-600">12+ languages</div>
              </div>
            </div>
            
            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow duration-300">
              <PhoneIcon className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <div className="font-semibold text-gray-900">Voice Support</div>
                <div className="text-sm text-gray-600">Speak naturally</div>
              </div>
            </div>
            
            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow duration-300">
              <ClockIcon className="h-8 w-8 text-purple-600 mr-3" />
              <div>
                <div className="font-semibold text-gray-900">Instant Response</div>
                <div className="text-sm text-gray-600">&lt; 2 seconds</div>
              </div>
            </div>
            
            <div className="flex items-center p-4 bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow duration-300">
              <MapPinIcon className="h-8 w-8 text-red-600 mr-3" />
              <div>
                <div className="font-semibold text-gray-900">Local Context</div>
                <div className="text-sm text-gray-600">Rural-specific</div>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section id="testimonials" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h3 className="text-4xl font-bold text-gray-900 mb-4">Real Stories, Real Impact</h3>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Hear from rural community members whose lives have been positively impacted by WellBot
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <div key={index} className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
                  <div className="flex items-center mb-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mr-4">
                      <UserIcon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900">{testimonial.name}</h4>
                      <p className="text-sm text-gray-600 flex items-center">
                        <MapPinIcon className="h-3 w-3 mr-1" />
                        {testimonial.location}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <StarIcon key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  
                  <p className="text-gray-700 italic leading-relaxed">"{testimonial.text}"</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="py-20 bg-white">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-4xl font-bold text-gray-900 mb-6">Bridging the Healthcare Gap</h3>
                <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                  Rural communities often face challenges accessing timely healthcare information and guidance. 
                  Our platform provides immediate access to health-related assistance, helping you make informed 
                  decisions about your wellbeing.
                </p>
                
                <div className="space-y-4 mb-8">
                  <div className="flex items-start">
                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-4 mt-0.5">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-1">24/7 Accessibility</h4>
                      <p className="text-gray-600">Healthcare guidance available anytime</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mr-4 mt-0.5">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-1">Cultural Sensitivity</h4>
                      <p className="text-gray-600">Understanding local customs and beliefs</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center mr-4 mt-0.5">
                      <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-1">Evidence-Based</h4>
                      <p className="text-gray-600">Information backed by medical research</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 p-6 rounded-r-lg">
                  <div className="flex items-start">
                    <ShieldCheckIcon className="h-6 w-6 text-blue-600 mr-3 mt-0.5" />
                    <div>
                      <p className="text-blue-800 font-medium mb-2">
                        <strong>Important Medical Disclaimer</strong>
                      </p>
                      <p className="text-blue-700 text-sm leading-relaxed">
                        This platform provides general health information and guidance only. 
                        Always consult with qualified healthcare professionals for medical diagnosis, treatment, and emergencies.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="relative">
                <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-3xl p-8 text-white relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                  <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-12 -translate-x-12"></div>
                  
                  <div className="relative">
                    <h4 className="text-2xl font-bold mb-6">Our Mission</h4>
                    <p className="text-blue-100 leading-relaxed mb-6">
                      To democratize healthcare access in rural India by providing instant, reliable, and culturally-appropriate 
                      health guidance through AI technology.
                    </p>
                    
                    <div className="space-y-4">
                      <div className="flex items-center">
                        <HeartIcon className="h-5 w-5 mr-3" />
                        <span>Serving 15,000+ users daily</span>
                      </div>
                      <div className="flex items-center">
                        <GlobeAltIcon className="h-5 w-5 mr-3" />
                        <span>Available in 12 Indian languages</span>
                      </div>
                      <div className="flex items-center">
                        <UserGroupIcon className="h-5 w-5 mr-3" />
                        <span>Trusted by rural communities</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-br from-gray-900 to-blue-900 text-white mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            {/* Brand Section */}
            <div className="md:col-span-2">
              <div className="flex items-center mb-6">
                <div className="relative">
                  <HeartIcon className="h-8 w-8 text-blue-400 mr-3 animate-pulse" />
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                  WellBot
                </span>
              </div>
              <p className="text-gray-300 mb-6 leading-relaxed max-w-md">
                Empowering rural communities across India with accessible, AI-powered healthcare guidance. 
                Breaking barriers, building healthier communities.
              </p>
              
              {/* Emergency Contact */}
              <div 
                onClick={handleEmergencyClick}
                className="bg-red-600/20 border border-red-500/30 rounded-lg p-4 mb-6 cursor-pointer hover:bg-red-600/30 transition-colors duration-300"
              >
                <div className="flex items-center mb-2">
                  <PhoneIcon className="h-5 w-5 text-red-400 mr-2" />
                  <span className="font-semibold text-red-300">Emergency Helpline</span>
                </div>
                <div className="text-2xl font-bold text-red-200">108</div>
                <div className="text-sm text-red-300">Available 24/7 across India</div>
              </div>
            </div>
            
            {/* Quick Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4 text-blue-300">Quick Access</h4>
              <ul className="space-y-3">
                <li>
                  <button
                    onClick={handleTryNowClick}
                    className="text-gray-300 hover:text-blue-400 transition-colors duration-300 flex items-center group"
                  >
                    <ChatBubbleLeftRightIcon className="h-4 w-4 mr-2 group-hover:animate-bounce" />
                    Start Chat
                  </button>
                </li>
                <li>
                  <a href="#features" className="text-gray-300 hover:text-blue-400 transition-colors duration-300">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#testimonials" className="text-gray-300 hover:text-blue-400 transition-colors duration-300">
                    Success Stories
                  </a>
                </li>
                <li>
                  <a href="#about" className="text-gray-300 hover:text-blue-400 transition-colors duration-300">
                    About Us
                  </a>
                </li>
              </ul>
            </div>
            
            {/* Support Languages */}
            <div>
              <h4 className="text-lg font-semibold mb-4 text-blue-300">Supported Languages</h4>
              <div className="grid grid-cols-2 gap-2 text-sm text-gray-300">
                <div>English</div>
                <div>हिन्दी</div>
                <div>বাংলা</div>
                <div>தமிழ்</div>
                <div>తెలుగు</div>
                <div>मराठी</div>
                <div>ગુજરાતી</div>
                <div>ಕನ್ನಡ</div>
                <div>മലയാളം</div>
                <div>ਪੰਜਾਬੀ</div>
                <div>ଓଡ଼ିଆ</div>
                <div>অসমীয়া</div>
              </div>
            </div>
          </div>
          
          {/* Bottom Section */}
          <div className="border-t border-gray-700 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="text-gray-400 text-sm mb-4 md:mb-0">
                © 2024 WellBot Platform. Built with ❤️ for rural communities across India.
              </div>
              
              <div className="flex items-center space-x-6 text-sm text-gray-400">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                  System Status: Online
                </div>
                <div className="flex items-center">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  24/7 Available
                </div>
                <div className="flex items-center">
                  <ShieldCheckIcon className="h-4 w-4 mr-1" />
                  Secure & Private
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>
      

    </div>
  );
};

export default LandingPage;
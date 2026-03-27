'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [cities, setCities] = useState([]);
  const [citiesAllLangs, setCitiesAllLangs] = useState([]);
  const [categoriesAllLangs, setCategoriesAllLangs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [language, setLanguage] = useState('en');
  const [selectedCity, setSelectedCity] = useState('');
  const [citySearchInput, setCitySearchInput] = useState('');
  const [showCityDropdown, setShowCityDropdown] = useState(false);
  const [uiStrings, setUiStrings] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  // Quick fix: Refresh page once when user reaches home page (prevents cached language issues)
  useEffect(() => {
    // Check if page was just loaded (not from back button cache)
    if (typeof window !== 'undefined') {
      const navigationEntries = window.performance?.getEntriesByType?.('navigation');
 
    }
  }, []);

  // Setup event listeners for syncing language on back button and page restore
  useEffect(() => {
    const syncFromStorage = () => {
      try {
        const savedLang = localStorage.getItem('language') || 'en';
        const savedCity = localStorage.getItem('selectedCity') || '';
        console.log('Syncing from storage:', savedLang, savedCity);
        setLanguage(savedLang);
        setSelectedCity(savedCity);
      } catch (e) {
        console.error('Error syncing from localStorage:', e);
      }
    };

    // Sync immediately on first load
    syncFromStorage();

    // Listen for page visibility changes (when tab becomes visible)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('Page became visible, syncing language');
        syncFromStorage();
      }
    };

    // Listen for pageshow event (back/forward button)
    const handlePageShow = (event) => {
      console.log('Page show event fired, persisted:', event.persisted);
      if (event.persisted) {
        // Force reload when page is restored from bfcache
        // This ensures fresh data with correct language
        window.location.reload();
      } else {
        syncFromStorage();
      }
    };

    // Listen for storage changes from other tabs
    const handleStorageChange = (e) => {
      if (e.key === 'language' || e.key === null) {
        console.log('Storage changed, syncing');
        syncFromStorage();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('pageshow', handlePageShow);
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('pageshow', handlePageShow);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Fetch data when language changes
  useEffect(() => {
    // Clear UI strings immediately to prevent showing old language
    setUiStrings({});
    
    // Fetch UI strings from LOV - always use current language
    fetch(`http://localhost:8000/api/v1/lov/?type=UI_HOME&language=${language}`)
      .then(res => res.json())
      .then(data => {
        const items = data.results || data || [];
        const stringsMap = {};
        items.forEach(item => {
          stringsMap[item.lic] = item.description;
        });
        setUiStrings(stringsMap);
      })
      .catch(err => console.error('Error fetching UI strings:', err));

    // Fetch cities in both languages for cross-language search
    Promise.all([
      fetch(`http://localhost:8000/api/v1/lov/?type=CITY&language=en`),
      fetch(`http://localhost:8000/api/v1/lov/?type=CITY&language=ta`)
    ])
      .then(([resEn, resTa]) => {
        return Promise.all([resEn.json(), resTa.json()]);
      })
      .then(([dataEn, dataTa]) => {
        let itemsEn = dataEn.results || dataEn || [];
        let itemsTa = dataTa.results || dataTa || [];
        
        // Create a map: lic -> { en: name, ta: name }
        const cityMap = {};
        itemsEn.forEach(item => {
          if (!cityMap[item.lic]) cityMap[item.lic] = {};
          cityMap[item.lic].en = item.display_name;
          cityMap[item.lic].order = item.order || 0;
        });
        itemsTa.forEach(item => {
          if (!cityMap[item.lic]) cityMap[item.lic] = {};
          cityMap[item.lic].ta = item.display_name;
        });
        
        // Store all cities for search
        const allCities = Object.entries(cityMap).map(([lic, names]) => ({
          id: lic,
          en: names.en || '',
          ta: names.ta || '',
          order: names.order || 0
        }));
        setCitiesAllLangs(allCities);
        
        // Create sorted list for selected language
        const sortedByOrder = allCities.sort((a, b) => {
          if (a.order !== b.order) return a.order - b.order;
          return (a[language] || '').localeCompare(b[language] || '');
        });
        setCities(sortedByOrder.map((item, index) => ({ 
          id: item.id, 
          name: item[language] || '',
          key: `${item.id}-${index}`
        })));
      })
      .catch(err => console.error('Error fetching cities:', err));

    // Fetch Categories in both languages (like cities)
    Promise.all([
      fetch(`http://localhost:8000/api/v1/lov/?type=CATEGORY&language=en`),
      fetch(`http://localhost:8000/api/v1/lov/?type=CATEGORY&language=ta`)
    ])
      .then(([resEn, resTa]) => {
        return Promise.all([resEn.json(), resTa.json()]);
      })
      .then(([dataEn, dataTa]) => {
        let itemsEn = dataEn.results || dataEn || [];
        let itemsTa = dataTa.results || dataTa || [];
        
        // Create a map: lic -> { en: name, ta: name }
        const categoryMap = {};
        itemsEn.forEach(item => {
          if (!categoryMap[item.lic]) categoryMap[item.lic] = {};
          categoryMap[item.lic].en = item.display_name;
          categoryMap[item.lic].order = item.order || 0;
        });
        itemsTa.forEach(item => {
          if (!categoryMap[item.lic]) categoryMap[item.lic] = {};
          categoryMap[item.lic].ta = item.display_name;
        });
        
        // Store all categories with both languages
        const allCategories = Object.entries(categoryMap).map(([lic, names]) => ({
          id: lic,
          slug: lic.toLowerCase(),
          en: names.en || '',
          ta: names.ta || '',
          order: names.order || 0
        }));
        setCategoriesAllLangs(allCategories);
        
        // Display in selected language
        const sortedCats = allCategories.sort((a, b) => a.order - b.order);
        setCategories(
          sortedCats.map(item => ({
            slug: item.slug,
            name: item[language] || item.en || ''
          }))
        );
      })
      .catch(err => console.error('Error fetching categories:', err));
  }, [language]);

  const handleCityChange = (e) => {
    const city = e.target.value;
    setSelectedCity(city);
    localStorage.setItem('selectedCity', city);
  };

  // Filter cities based on search input (search in both EN and TA, display in selected language)
  const filteredCities = citiesAllLangs.filter(city => {
    const searchLower = citySearchInput.toLowerCase();
    // Search in English name, Tamil name, or LIC (for cross-language support)
    const matchesEn = (city.en || '').toLowerCase().includes(searchLower);
    const matchesTa = (city.ta || '').toLowerCase().includes(searchLower);
    const matchesLic = city.id.toLowerCase().includes(searchLower);
    return matchesEn || matchesTa || matchesLic;
  }).map(city => ({
    id: city.id,
    // Display in selected language, fallback to other language if not available
    name: city[language] || city[language === 'en' ? 'ta' : 'en'] || '',
    key: city.id
  }));

  const handleCitySelectFromDropdown = (cityId, cityName) => {
    setSelectedCity(cityId);
    setCitySearchInput(cityName);
    setShowCityDropdown(false);
    localStorage.setItem('selectedCity', cityId);
  };

  // Get the display name of the selected city
  const getSelectedCityName = () => {
    if (!selectedCity) return 'None selected';
    const selectedCityObj = citiesAllLangs.find(c => c.id === selectedCity);
    return selectedCityObj ? (selectedCityObj[language] || selectedCityObj.en || selectedCityObj.ta || selectedCity) : selectedCity;
  };

  const changeLanguage = (lang) => {
    localStorage.setItem('language', lang);
    document.cookie = `language=${lang}; path=/; max-age=31536000`;
    setLanguage(lang);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--paper-bg)' }}>
      {/* NEWSPAPER MASTHEAD */}
      <header className="header" style={{ 
        backgroundColor: 'var(--ink-black)', 
        color: 'var(--paper-bg)',
        padding: '1.5rem 0',
        borderBottom: '4px solid var(--accent-yellow)'
      }}>
        <div className="container">
          <div style={{ textAlign: 'left' }}>
            <h1 style={{ 
              fontSize: '2.5rem', 
              margin: 0, 
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: 'var(--paper-bg)'
            }}>
              {uiStrings.SITE_TITLE || 'Daily Classifieds'}
              <span style={{ 
                fontSize: '0.8rem',   // smaller size
               // verticalAlign: 'super',
                marginLeft: '4px',
                letterSpacing: '0.05em'
              }}>
                .com
              </span>
            </h1>
          </div>
        </div>
      </header>

      {/* NAVIGATION BAR */}
      <div style={{ 
        backgroundColor: 'var(--paper-dark)', 
        borderBottom: '2px solid var(--border-gray)',
        padding: '0.75rem 0'
      }}>
        <div className="container">
          <div className="nav-section" style={{ 
            display: 'flex', 
            justifyContent: 'center',
            gap: '1.5rem',
            flexWrap: 'wrap',
            border: 'none',
            padding: 0,
            margin: 0
          }}>
            <Link href="/post" className="btn" style={{ textDecoration: 'none' }}>
              {uiStrings.POST_AD_BUTTON || 'Post an Ad'}
            </Link>
            <span style={{ color: 'var(--ink-light)' }}>|</span>
            <button
              onClick={() => changeLanguage('en')}
              className={`lang-btn ${language === 'en' ? 'active' : ''}`}
              suppressHydrationWarning
            >
              {uiStrings.LANGUAGE_EN || 'English'}
            </button>
            <button
              onClick={() => changeLanguage('ta')}
              className={`lang-btn ${language === 'ta' ? 'active' : ''}`}
              suppressHydrationWarning
            >
              {uiStrings.LANGUAGE_TA || 'தமிழ்'}
            </button>
            {selectedCity && (
              <>
                <span style={{ color: 'var(--ink-light)' }}>|</span>
                <span className="badge" style={{ fontSize: '0.85rem' }}>
                  {getSelectedCityName()}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <main style={{ padding: '2rem 0' }}>
        <div className="container">
          {/* CITY SELECTION SECTION */}
          <div style={{ 
            backgroundColor: 'var(--paper-dark)', 
            padding: '1.5rem',
            borderTop: '3px double var(--border-gray)',
            borderBottom: '3px double var(--border-gray)',
            marginBottom: '2rem'
          }}>
            <h6 style={{ 
              textAlign: 'center', 
              marginBottom: '1rem',
              fontSize: '1.25rem',
              textTransform: 'uppercase',
              letterSpacing: '0.1em'
            }}>
              {uiStrings.SELECT_CITY_HEADER || 'Select Your City'}
            </h6>
            
            <div style={{ maxWidth: '400px', margin: '0 auto', position: 'relative' }}>
              <input 
                type="text" 
                value={citySearchInput}
                onChange={e => {
                  setCitySearchInput(e.target.value);
                  setShowCityDropdown(true);
                }}
                onFocus={() => { setShowCityDropdown(true); setCitySearchInput(''); }}
                onBlur={() => setTimeout(() => setShowCityDropdown(false), 200)}
                placeholder={uiStrings.CITY_SEARCH_PLACEHOLDER || 'Search for your city...'}
                className="input"
                style={{ textAlign: 'center', fontSize: '1.1rem' }}
                autoComplete="off"
              />
              {showCityDropdown && (
                <ul className="select-dropdown" style={{ 
                  position: 'absolute', 
                  top: '100%', 
                  left: 0, 
                  right: 0, 
                  zIndex: 10, 
                  marginTop: '0.25rem',
                  backgroundColor: 'white',
                  border: '2px solid var(--border-gray)',
                  maxHeight: '250px',
                  overflowY: 'auto'
                }}>
                  <li onClick={() => handleCitySelectFromDropdown('', uiStrings.ALL_CITIES || 'All Cities')} style={{ padding: '0.75rem', borderBottom: '1px solid var(--border-light)', cursor: 'pointer' }}>
                    <strong>{uiStrings.ALL_CITIES || 'All Cities'}</strong>
                  </li>
                  {filteredCities.length > 0 ? (
                    filteredCities.map(c => (
                      <li key={c.key} onClick={() => handleCitySelectFromDropdown(c.id, c.name)} style={{ padding: '0.75rem', borderBottom: '1px solid var(--border-light)', cursor: 'pointer' }}>
                        {c.name}
                      </li>
                    ))
                  ) : (
                    <li style={{ padding: '0.75rem', color: 'var(--ink-light)' }}>{uiStrings.NO_CITIES_FOUND || 'No cities found'}</li>
                  )}
                </ul>
              )}
            </div>
			{/*
            <p style={{ 
              textAlign: 'center', 
              marginTop: '1rem',
              fontSize: '0.9rem',
              color: 'var(--ink-light)',
              fontStyle: 'italic'
            }}>
              {cities.length} {uiStrings.CITIES_AVAILABLE || 'cities available'}
            </p>*/}
          </div>

          {/* CATEGORIES SECTION */}
          <div>
            <h2 className="category-header" style={{ marginTop: 0 }}>
              {uiStrings.BROWSE_CATEGORIES_HEADER || 'Browse Categories'}
            </h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '1rem',
              marginTop: '1.5rem'
            }}>
              {categories.map(cat => (
                <Link
                  key={cat.slug}
                  href={{
                    pathname: `/category/${cat.slug}`,
                    query: selectedCity ? { city: selectedCity } : {},
                  }}
                  className="btn btn-secondary"
                  style={{ 
                    textAlign: 'center', 
                    padding: '1rem',
                    textDecoration: 'none',
                    display: 'block'
                  }}
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </div>

          {/* FOOTER */}
          <div style={{ 
            marginTop: '3rem', 
            paddingTop: '1.5rem',
            borderTop: '1px solid var(--border-light)',
            textAlign: 'center'
          }}>
            <p style={{ 
              fontSize: '0.85rem', 
              color: 'var(--ink-light)',
              fontStyle: 'italic'
            }}>
              {uiStrings.COPYRIGHT_PREFIX || '© 2025 Daily Classifieds'} • {uiStrings.POST_YOUR_AD_TODAY || 'Post your ad today'}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

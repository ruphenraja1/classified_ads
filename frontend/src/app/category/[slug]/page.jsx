'use client';

import Link from 'next/link';
import { useState, useEffect, use } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

function safeSearchParams(obj = {}) {
  return Object.fromEntries(
    Object.entries(obj).filter(
      ([, v]) => typeof v === 'string'
    )
  );
}

export default function Page({ params }) {
  const { slug } = use(params);
  const searchParams = useSearchParams();
  const router = useRouter();
  const resolvedSearchParams = Object.fromEntries(searchParams.entries());

  const [ads, setAds] = useState([]);
  const [cities, setCities] = useState([]);
  const [citiesAllLangs, setCitiesAllLangs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categorySlug, setCategorySlug] = useState(slug);
  const [city, setCity] = useState(searchParams.get('city') || '');
  const [sort, setSort] = useState(searchParams.get('sort') || 'newest');
  const [posted, setPosted] = useState(searchParams.get('posted') || '');
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [searchInput, setSearchInput] = useState(searchParams.get('search') || '');
  const [page, setPage] = useState(searchParams.get('page') || '1');
  const [cityMap, setCityMap] = useState({});
  const [categoryMapDisplay, setCategoryMapDisplay] = useState({});
  const [totalAds, setTotalAds] = useState(0);
  const [todaysAdsCount, setTodaysAdsCount] = useState(0);
  const [citySearchInput, setCitySearchInput] = useState('');
  const [showCityDropdown, setShowCityDropdown] = useState(false);
  const [language, setLanguage] = useState('en');

  // Sync state with URL params
  useEffect(() => {
    setCity(searchParams.get('city') || '');
    setSort(searchParams.get('sort') || 'newest');
    setPosted(searchParams.get('posted') || '');
    setSearch(searchParams.get('search') || '');
    setSearchInput(searchParams.get('search') || '');
    setPage(searchParams.get('page') || '1');
  }, [searchParams]);

  // Sync language when returning from another page (back button)
  useEffect(() => {
    const syncLanguageFromStorage = () => {
      try {
        const savedLang = localStorage.getItem('language') || 'en';
        console.log('Category page syncing language:', savedLang);
        setLanguage(savedLang);
      } catch (e) {
        console.error('Error syncing from localStorage:', e);
      }
    };

    // Sync immediately
    syncLanguageFromStorage();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        console.log('Category page became visible, syncing');
        syncLanguageFromStorage();
      }
    };

    const handlePageShow = (event) => {
      console.log('Category page show event fired, persisted:', event.persisted);
      syncLanguageFromStorage();
    };

    const handleStorageChange = (e) => {
      if (e.key === 'language' || e.key === null) {
        console.log('Category storage changed, syncing');
        syncLanguageFromStorage();
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

  useEffect(() => {
    const fetchData = async () => {
      const lang = localStorage.getItem('language') || 'en';
      setLanguage(lang);

      // Fetch cities in both languages for cross-language search
      const [citiesEnRes, citiesTaRes, categoriesRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/lov/?type=CITY&language=en`),
        fetch(`http://localhost:8000/api/v1/lov/?type=CITY&language=ta`),
        fetch(`http://localhost:8000/api/v1/lov/?type=CATEGORY&language=${lang}`)
      ]);

      const citiesEnResponse = citiesEnRes.ok ? await citiesEnRes.json() : { results: [] };
      const citiesTaResponse = citiesTaRes.ok ? await citiesTaRes.json() : { results: [] };
      const categoriesResponse = categoriesRes.ok ? await categoriesRes.json() : { results: [] };

      let itemsEn = citiesEnResponse.results || [];
      let itemsTa = citiesTaResponse.results || [];
      const categoriesData = categoriesResponse.results || [];

      // Create a map: lic -> { en: name, ta: name }
      const cityMap2 = {};
      itemsEn.forEach(item => {
        if (!cityMap2[item.lic]) cityMap2[item.lic] = {};
        cityMap2[item.lic].en = item.display_name;
        cityMap2[item.lic].order = item.order || 0;
      });
      itemsTa.forEach(item => {
        if (!cityMap2[item.lic]) cityMap2[item.lic] = {};
        cityMap2[item.lic].ta = item.display_name;
      });

      // Store all cities for search
      const allCitiesData = Object.entries(cityMap2).map(([lic, names]) => ({
        id: lic,
        en: names.en || '',
        ta: names.ta || '',
        order: names.order || 0,
        lic: lic
      }));
      
      // Sort by order
      allCitiesData.sort((a, b) => {
        if (a.order !== b.order) return a.order - b.order;
        return (a[lang] || '').localeCompare(b[lang] || '');
      });

      setCitiesAllLangs(allCitiesData);
      setCities(allCitiesData.map(c => ({ lic: c.lic, display_name: c[lang] || '' })));

      const cityMapTemp = {};
      allCitiesData.forEach(c => cityMapTemp[c.lic] = c[lang] || '');
      setCityMap(cityMapTemp);

      const categoryMapDisplayTemp = {};
      categoriesData.forEach(c => categoryMapDisplayTemp[c.lic] = c.display_name);
      setCategoryMapDisplay(categoryMapDisplayTemp);

      setCategories(categoriesData);

      // Fetch ads
      const apiUrl = 'http://localhost:8000/api/v1/ads/';
      const paramsQs = new URLSearchParams();
      paramsQs.append('category', slug);
      if (sort) paramsQs.append('sort', sort);
      if (city) paramsQs.append('city', city);
      if (posted) paramsQs.append('posted', posted);
      if (search) paramsQs.append('search', search);
      if (page) paramsQs.append('page', page);
      
      const res = await fetch(`${apiUrl}?${paramsQs}`);
      const adsData = res.ok ? await res.json() : { results: [] };
      
      // Apply client-side sorting if needed
      let sortedAds = adsData.results || [];
      if (sort === 'oldest') {
        sortedAds = [...sortedAds].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      } else if (sort === 'price_asc') {
        sortedAds = [...sortedAds].sort((a, b) => (a.price || 0) - (b.price || 0));
      } else if (sort === 'price_desc') {
        sortedAds = [...sortedAds].sort((a, b) => (b.price || 0) - (a.price || 0));
      } else {
        // Default to newest first
        sortedAds = [...sortedAds].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      }

      setAds(sortedAds);
      setTotalAds(adsData.count || 0);

      // Today's ads counts
      const todaysParams = new URLSearchParams({ category: slug });
      if (city) todaysParams.append('city', city);
      todaysParams.append('posted', '1');
      todaysParams.append('page', '1');
      const todaysRes = await fetch(`http://localhost:8000/api/v1/ads/?${todaysParams}`);
      const todaysData = todaysRes.ok ? await todaysRes.json() : { count: 0 };
      setTodaysAdsCount(todaysData.count || todaysData.results?.length || 0);

      setLoading(false);
    };

    fetchData();
  }, [slug, city, sort, posted, search, page, language]);

  // Function to update URL with new params
  const updateURL = (updates) => {
    const params = new URLSearchParams(window.location.search);

    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });

    router.push(`?${params.toString()}`);
  };

  // Handle posted filter change
  const handlePostedChange = (value) => {
    updateURL({ posted: value, page: '1' });
  };

  // Handle sort change
  const handleSortChange = (value) => {
    updateURL({ sort: value });
  };

  // Handle page change
  const handlePageChange = (newPage) => {
    updateURL({ page: newPage.toString() });
  };

  // Handle search form submission
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    updateURL({ search: searchInput, page: '1' });
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-2xl" style={{ color: 'var(--color-text-muted)' }}>Loading...</div>
    </div>
  );

  // Resolve category display name from LIC mapping or slug
  let displayFromLic = null;
  const slugLower = slug ? slug.toLowerCase() : '';
  for (const c of categories) {
    const lic = (c.lic || '').toLowerCase();
    if (lic === slugLower || lic === slugLower.replace(/-/g, '_')) {
      displayFromLic = c.display_name;
      break;
    }
  }
  const slugDisplayName = slugLower
    .split('_')
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join(' ');
  const categoryDisplay = displayFromLic || (categoryMapDisplay[slug] || slugDisplayName);
  const cityDisplay = cityMap[city] || city;
  const citySuffix = cityDisplay ? ` - ${cityDisplay}` : '';

  const pageNum = parseInt(page, 10);
  const totalPages = Math.ceil(totalAds / 20);

  // Filter cities based on search input (search in both EN and TA, display in selected language)
  const filteredCities = citiesAllLangs.filter(city => {
    const searchLower = citySearchInput.toLowerCase();
    // Search in English name, Tamil name, or LIC (for cross-language support)
    const matchesEn = (city.en || '').toLowerCase().includes(searchLower);
    const matchesTa = (city.ta || '').toLowerCase().includes(searchLower);
    const matchesLic = city.id.toLowerCase().includes(searchLower);
    return matchesEn || matchesTa || matchesLic;
  }).map(city => ({
    lic: city.id,
    // Display in selected language, fallback to other language if not available
    display_name: city[language] || city[language === 'en' ? 'ta' : 'en'] || '',
    key: city.id
  }));

  const handleCitySelectFromDropdown = (cityLic, cityName) => {
    setCitySearchInput(''); // Clear search input after selection
    setShowCityDropdown(false);
    updateURL({ city: cityLic, page: '1' });
  };

  return (
    <div className="min-h-screen">
      {/* Newspaper Masthead */}
      <header className="header">
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Link href="/" style={{ textDecoration: 'none' }}>
              <h1 style={{ margin: 0 }}>VARIVILAMBARANGAL</h1>
            </Link>
            <div style={{ textAlign: 'right' }}>
              <p style={{ margin: 0, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                {categoryDisplay}{citySuffix}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main style={{ padding: '1rem 0' }}>
        <div className="container">
          {/* Newspaper Filter Section */}
          <div className="filter-section">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {/* Top Row: Date Filters + Results Count */}
              <div style={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                gap: '0.75rem', 
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase' }}>Posted:</span>
                  {[
                    { label: 'Today', value: '1' },
                    { label: '3d', value: '3' },
                    { label: '7d', value: '7' },
                    { label: '30d', value: '30' },
                  ].map(({ label, value }) => (
                    <button
                      key={value}
                      onClick={() => handlePostedChange(value)}
                      className={posted === value ? 'btn' : 'btn btn-secondary'}
                      style={{ padding: '0.375rem 0.625rem', fontSize: '0.8rem' }}
                    >
                      {label}
                    </button>
                  ))}
                  {posted && (
                    <button
                      onClick={() => handlePostedChange('')}
                      className="btn btn-secondary"
                      style={{ padding: '0.375rem 0.625rem', fontSize: '0.8rem' }}
                    >
                      Clear
                    </button>
                  )}
                </div>
                
                {/* Results Count */}
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span className="badge">{totalAds} ads</span>
                  {todaysAdsCount > 0 && (
                    <span className="badge">{todaysAdsCount} new</span>
                  )}
                </div>
              </div>

              {/* Bottom Row: Sort + Search */}
              <div style={{ 
                display: 'flex', 
                flexWrap: 'wrap',
                gap: '0.75rem',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase' }}>Sort:</span>
                  <button
                    onClick={() => handleSortChange('newest')}
                    className={sort === 'newest' ? 'btn' : 'btn btn-secondary'}
                    style={{ padding: '0.375rem 0.625rem', fontSize: '0.8rem' }}
                  >
                    Newest
                  </button>
                  <button
                    onClick={() => handleSortChange('oldest')}
                    className={sort === 'oldest' ? 'btn' : 'btn btn-secondary'}
                    style={{ padding: '0.375rem 0.625rem', fontSize: '0.8rem' }}
                  >
                    Oldest
                  </button>
                </div>

                {/* Search Form */}
                <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="text"
                    name="search"
                    placeholder="Search ads..."
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    maxLength="32"
                    className="input"
                    style={{ minWidth: '180px', padding: '0.375rem 0.625rem', fontSize: '0.9rem' }}
                  />
                  <button type="submit" className="btn" style={{ padding: '0.375rem 0.625rem', fontSize: '0.8rem' }}>
                    Find
                  </button>
                </form>
              </div>
            </div>
          </div>

          {/* Category Header */}
          <div className="category-header">
            {categoryDisplay} CLASSIFIEDS
          </div>

          {/* Classifieds Columns */}
          {ads.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', fontStyle: 'italic', color: 'var(--ink-light)' }}>
              No ads found. Try adjusting your filters.
            </div>
          ) : (
            <div className="classifieds-columns">
              {ads.map((ad) => (
                <div key={ad.id} className="classified-ad">
                  <Link href={`/ad/${ad.id}`} style={{ textDecoration: 'none' }}>
                    <div className="ad-title">
                      {ad.title.length > 80 ? ad.title.substring(0, 80) + '...' : ad.title}
                    </div>
                  </Link>
                  
                  <div className="ad-description">
                    {ad.description.length > 150
                      ? `${ad.description.substring(0, 150)}...`
                      : ad.description
                    }
                    {ad.description.length > 150 && (
                      <Link href={`/ad/${ad.id}`} style={{ fontWeight: 700 }}>
                        More
                      </Link>
                    )}
                  </div>
                  
                  <div className="ad-meta" style={{ marginBottom: '0.5rem' }}>
                    {ad.location.length > 60 ? ad.location.substring(0, 60) + '...' : ad.location}
                  </div>

                  <div className="ad-meta">
                    <a href={`tel:${ad.phone}`} className="phone-number">
                      {ad.phone}
                    </a>
                    {ad.whatsapp && (
                      <span style={{ marginLeft: '0.75rem' }}>
                        <a href={`https://wa.me/${ad.whatsapp}`} style={{ textDecoration: 'none' }}>
                          [WhatsApp]
                        </a>
                      </span>
                    )}
                  </div>
                  
                  <div className="ad-meta" style={{ marginTop: '0.25rem' }}>
                    Posted: {new Date(ad.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              {pageNum > 1 && (
                <button
                  onClick={() => handlePageChange(pageNum - 1)}
                  className="btn btn-secondary"
                >
                  ← Prev
                </button>
              )}

              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const p = Math.max(1, pageNum - 2) + i;
                if (p > totalPages) return null;

                return (
                  <button
                    key={p}
                    onClick={() => handlePageChange(p)}
                    className={p === pageNum ? 'btn' : 'btn btn-secondary'}
                    style={{ minWidth: '36px' }}
                  >
                    {p}
                  </button>
                );
              })}

              {pageNum < totalPages && (
                <button
                  onClick={() => handlePageChange(pageNum + 1)}
                  className="btn btn-secondary"
                >
                  Next →
                </button>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

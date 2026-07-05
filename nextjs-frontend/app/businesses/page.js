'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '../components/ToastProvider';
import Spinner from '../components/Spinner';

const CATEGORIES = {
  "Retail & Shopping": ["Grocery", "Supermarket", "Clothing", "Shoes", "Electronics", "Mobile Phone", "Jewellery", "Bookstore", "Florist"],
  "Education": ["School", "University", "College", "Kindergarten", "Language School", "Driving School"],
  "Services": ["Laundry", "Car Wash", "Car Repair", "Petrol", "Parking"],
  "Accommodation": ["Hotel", "Hostel", "Motel", "Guest House"],
  "Finance": ["Bank", "ATM", "Money Exchange"],
  "Fitness & Beauty": ["Gym", "Fitness", "Salon", "Hair Salon", "Beauty Salon", "Spa", "Barber"],
  "Food & Drink": ["Restaurant", "Cafe", "Coffee", "Fast Food", "Bar", "Pub", "Bakery", "Pizza", "Ice Cream"],
  "Health": ["Dentist", "Doctor", "Clinic", "Hospital", "Pharmacy", "Optician", "Physiotherapy"]
};

export default function BusinessesPage() {
  const showToast = useToast();
  const router = useRouter();

  // Search state
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [radius, setRadius] = useState(8000);
  const [limit, setLimit] = useState(100);
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);

  // Saved businesses state
  const [businesses, setBusinesses] = useState([]);
  const [bizLoading, setBizLoading] = useState(false);

  // Modal state
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [savingBusiness, setSavingBusiness] = useState(null);
  const [saveForm, setSaveForm] = useState({ email: '', phone: '', notes: '' });

  // Crawl state
  const [crawling, setCrawling] = useState({});

  // Tab state
  const [activeTab, setActiveTab] = useState('search');

  const resultsRef = useRef([]);
  useEffect(() => {
    resultsRef.current = results;
  }, [results]);

  const [findingState, setFindingState] = useState('idle'); // 'idle', 'running', 'paused'
  const findingIndexRef = useRef(0);
  const findingStateRef = useRef('idle');
  const findingFoundRef = useRef(0);
  const [findingProcessedCount, setFindingProcessedCount] = useState(0);
  const [findingFoundCount, setFindingFoundCount] = useState(0);

  const [crawlingState, setCrawlingState] = useState('idle'); // 'idle', 'running', 'paused'
  const crawlingIndexRef = useRef(0);
  const crawlingStateRef = useRef('idle');
  const crawlingFoundRef = useRef(0);
  const [crawlingProcessedCount, setCrawlingProcessedCount] = useState(0);
  const [crawlingFoundCount, setCrawlingFoundCount] = useState(0);

  function updateFindingState(newState) {
    setFindingState(newState);
    findingStateRef.current = newState;
  }

  function updateCrawlingState(newState) {
    setCrawlingState(newState);
    crawlingStateRef.current = newState;
  }

  async function toggleFindWebsites() {
    if (findingState === 'idle') {
      updateFindingState('running');
      findingIndexRef.current = 0;
      findingFoundRef.current = 0;
      setFindingProcessedCount(0);
      setFindingFoundCount(0);
      processFindWebsites();
    } else if (findingState === 'running') {
      updateFindingState('paused');
    } else if (findingState === 'paused') {
      updateFindingState('running');
      processFindWebsites();
    }
  }

  async function processFindWebsites() {
    while (findingIndexRef.current < resultsRef.current.length) {
      if (findingStateRef.current !== 'running') break;
      
      const idx = findingIndexRef.current;
      const biz = resultsRef.current[idx];
      if (!biz) break;
      
      if (!biz.website) {
        try {
          const cityVal = location.includes(',') ? location.split(',')[0].trim() : location.trim();
          const countryVal = location.includes(',') ? location.split(',').pop().trim() : '';
          
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 45000); // 45s timeout
          
          const res = await fetch('/api/v1/businesses/discover-website-single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              business_name: biz.business_name || biz.name || biz.display_name || '',
              city: cityVal,
              country: countryVal
            }),
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (res.ok) {
            const data = await res.json();
            if (data.website) {
              findingFoundRef.current++;
              setFindingFoundCount(findingFoundRef.current);
            }
            setResults(prev => {
              const updated = [...prev];
              const b = updated[idx];
              if (!b) return prev;
              updated[idx] = { 
                ...b, 
                website: data.website || b.website, 
                facebook: data.facebook || b.facebook, 
                instagram: data.instagram || b.instagram, 
                crawled_email: data.email || b.crawled_email, 
                phone: data.phone || b.phone,
                source_website: (!b.website && data.website) ? 'directory' : b.source_website,
                source_facebook: (!b.facebook && data.facebook) ? 'directory' : b.source_facebook,
                source_instagram: (!b.instagram && data.instagram) ? 'directory' : b.source_instagram,
                source_email: (!b.crawled_email && data.email) ? 'directory' : b.source_email,
                source_phone: (!b.phone && data.phone) ? 'directory' : b.source_phone,
              };
              return updated;
            });
          }
        } catch (e) {
          console.error(e);
        }
      }
      findingIndexRef.current++;
      setFindingProcessedCount(findingIndexRef.current);
      // 0.8s between requests (backend is optimized, DDG just needs brief gaps)
      await new Promise(resolve => setTimeout(resolve, 800));
    }
    
    if (findingStateRef.current === 'running' && findingIndexRef.current >= resultsRef.current.length) {
      updateFindingState('idle');
      showToast('Finished finding websites', 'success');
    }
  }

  async function toggleCrawlWebsites() {
    if (crawlingState === 'idle') {
      updateCrawlingState('running');
      crawlingIndexRef.current = 0;
      crawlingFoundRef.current = 0;
      setCrawlingProcessedCount(0);
      setCrawlingFoundCount(0);
      processCrawlWebsites();
    } else if (crawlingState === 'running') {
      updateCrawlingState('paused');
    } else if (crawlingState === 'paused') {
      updateCrawlingState('running');
      processCrawlWebsites();
    }
  }

  async function processCrawlWebsites() {
    while (crawlingIndexRef.current < resultsRef.current.length) {
      if (crawlingStateRef.current !== 'running') break;
      
      const idx = crawlingIndexRef.current;
      const biz = resultsRef.current[idx];
      if (!biz) break;
      
      if (biz.website && (!biz.crawled_email || !biz.facebook || !biz.instagram || !biz.phone)) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 20000); // 20s timeout
          
          const res = await fetch('/api/v1/businesses/crawl-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: biz.website, use_playwright: false }),
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (res.ok) {
            const data = await res.json();
            if (data.email || data.phone || data.facebook || data.instagram) {
              crawlingFoundRef.current++;
              setCrawlingFoundCount(crawlingFoundRef.current);
            }
            setResults(prev => {
              const updated = [...prev];
              const b = updated[idx];
              if (!b) return prev;
              updated[idx] = { 
                ...b, 
                crawled_email: data.email || b.crawled_email, 
                facebook: data.facebook || b.facebook, 
                instagram: data.instagram || b.instagram, 
                phone: data.phone || b.phone,
                source_facebook: (!b.facebook && data.facebook) ? 'website' : b.source_facebook,
                source_instagram: (!b.instagram && data.instagram) ? 'website' : b.source_instagram,
                source_email: (!b.crawled_email && data.email) ? 'website' : b.source_email,
                source_phone: (!b.phone && data.phone) ? 'website' : b.source_phone,
              };
              return updated;
            });
          }
        } catch (e) {
          console.error(e);
        }
      }
      crawlingIndexRef.current++;
      setCrawlingProcessedCount(crawlingIndexRef.current);
      // 0.3s between crawl requests (httpx-based, fast)
      await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    if (crawlingStateRef.current === 'running' && crawlingIndexRef.current >= resultsRef.current.length) {
      updateCrawlingState('idle');
      showToast('Finished crawling websites', 'success');
    }
  }

  useEffect(() => {
    loadSavedBusinesses();
  }, []);

  async function searchBusinesses() {
    if (!query.trim()) {
      showToast('Please select a business type', 'warning');
      return;
    }
    if (!location.trim()) {
      showToast('Please enter a location (e.g., "New York, US" or "London, UK")', 'warning');
      return;
    }

    setSearching(true);
    setResults([]);

    try {
      let city = location.trim();
      let country = ''; // default to empty if not specified
      
      if (location.includes(',')) {
        const parts = location.split(',');
        city = parts[0].trim();
        country = parts[parts.length - 1].trim();
      }

      const payload = {
        business_type: query,
        city: city,
        country: country,
        radius_meters: radius,
        enable_website_crawl: false
      };

      const response = await fetch('/api/v1/osm/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
        const totalCount = data.result_count || data.total || 0;
        setTotal(totalCount);
        showToast(`Found ${totalCount} businesses`, 'success');
      } else {
        const error = await response.json();
        showToast(error.detail || 'Search failed', 'error');
      }
    } catch (error) {
      showToast('Search failed: ' + error.message, 'error');
    } finally {
      setSearching(false);
    }
  }

  async function loadSavedBusinesses() {
    setBizLoading(true);
    try {
      const res = await fetch('/api/v1/businesses?per_page=100');
      if (res.ok) {
        const data = await res.json();
        setBusinesses(data.businesses || []);
      }
    } catch (error) {
      console.error('Failed to load businesses:', error);
    } finally {
      setBizLoading(false);
    }
  }

  function openSaveModal(biz) {
    setSavingBusiness(biz);
    setSaveForm({ email: '', phone: biz.phone || '', notes: '' });
    setShowSaveModal(true);
  }

  async function saveBusiness() {
    if (!savingBusiness) return;
    try {
      const payload = {
        business_name: savingBusiness.name || savingBusiness.display_name,
        website: savingBusiness.website || '',
        email: saveForm.email || null,
        phone: saveForm.phone || savingBusiness.phone || null,
        address: savingBusiness.address || '',
        city: savingBusiness.city || '',
        country: savingBusiness.country || '',
        category: savingBusiness.category || '',
        notes: saveForm.notes || null,
        lat: savingBusiness.lat || null,
        lon: savingBusiness.lon || null,
      };

      const response = await fetch('/api/v1/businesses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        showToast('Business saved!', 'success');
        setShowSaveModal(false);
        setSavingBusiness(null);
        loadSavedBusinesses();
      } else {
        const error = await response.json();
        showToast(error.detail || 'Failed to save', 'error');
      }
    } catch (error) {
      showToast('Failed to save: ' + error.message, 'error');
    }
  }

  async function crawlForEmail(biz, index) {
    if (!biz.website) {
      showToast('No website URL available', 'warning');
      return;
    }

    setCrawling(prev => ({ ...prev, [index]: true }));
    try {
      const response = await fetch('/api/v1/businesses/crawl-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: biz.website }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.email || (data.all_emails && data.all_emails.length > 0)) {
          const foundEmail = data.email || data.all_emails[0];
          const updated = [...results];
          updated[index] = { ...updated[index], crawled_email: foundEmail, source_email: 'website' };
          setResults(updated);
          showToast(`Found email: ${foundEmail}`, 'success');
        } else {
          showToast('No email found', 'warning');
        }
      } else {
        showToast('Crawl failed', 'error');
      }
    } catch (error) {
      showToast('Crawl failed: ' + error.message, 'error');
    } finally {
      setCrawling(prev => ({ ...prev, [index]: false }));
    }
  }

  async function deleteBusiness(id) {
    if (!confirm('Delete this business?')) return;
    try {
      const res = await fetch(`/api/v1/businesses/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('Business deleted', 'success');
        loadSavedBusinesses();
      } else {
        showToast('Delete failed', 'error');
      }
    } catch (error) {
      showToast('Delete failed', 'error');
    }
  }

  function goToAudit(biz) {
    sessionStorage.setItem('auditBusiness', JSON.stringify(biz));
    router.push(`/audits?website=${encodeURIComponent(biz.website)}`);
  }

  function goToOutreach(biz) {
    sessionStorage.setItem('selectedBusiness', JSON.stringify(biz));
    router.push('/outreach');
  }

  return (
    <div>
      {/* Tab Switcher */}
      <div className="flex space-x-2 mb-6 bg-white dark:bg-white/[0.015] rounded-xl p-1 border border-slate-200/80 dark:border-white/[0.06] w-fit">
        <button onClick={() => setActiveTab('search')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'search' ? 'bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white' : 'text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:text-white'}`}>
          🔍 Search OSM
        </button>
        <button onClick={() => setActiveTab('saved')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'saved' ? 'bg-[#6D5DF6] dark:bg-[#6D5DF6] text-white' : 'text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:text-white'}`}>
          💾 Saved ({businesses.length})
        </button>
      </div>

      {/* Search Tab */}
      {activeTab === 'search' && (
        <>
          {/* Search Form */}
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none mb-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Hunt Businesses</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Business Type</label>
                <select value={query} onChange={e => setQuery(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] transition-colors">
                  <option value="" disabled>Select a business type...</option>
                  {Object.entries(CATEGORIES).map(([category, items]) => (
                    <optgroup key={category} label={category} className="bg-slate-100 dark:bg-white/[0.04] text-slate-500 dark:text-[#8E8BA3] font-semibold">
                      {items.map(item => (
                        <option key={item} value={item.toLowerCase()} className="text-slate-900 dark:text-white font-normal bg-slate-100 dark:bg-[#08061a]">
                          {item}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Location</label>
                <input value={location} onChange={e => setLocation(e.target.value)} onKeyDown={e => e.key === 'Enter' && searchBusinesses()} type="text" placeholder="City or address..."
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] transition-colors" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Radius (m)</label>
                <select value={radius} onChange={e => setRadius(Number(e.target.value))}
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA] transition-colors">
                  <option value={500}>0.5 km</option>
                  <option value={1000}>1 km</option>
                  <option value={2000}>2 km</option>
                  <option value={5000}>5 km</option>
                  <option value={8000}>8 km</option>
                  <option value={15000}>15 km</option>
                  <option value={30000}>30 km</option>
                  <option value={50000}>50 km</option>
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={searchBusinesses} disabled={searching}
                  className="w-full bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white font-semibold py-2.5 px-4 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center">
                  {searching ? <><Spinner className="mr-2 h-4 w-4" /> Searching...</> : '🔍 Search'}
                </button>
              </div>
            </div>
          </div>

          {/* Search Results */}
          {results.length > 0 && (
            <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Results ({total})</h3>
                <div className="flex space-x-2">
                  <button onClick={toggleFindWebsites}
                    className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${findingState === 'running' ? 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30' : findingState === 'paused' ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30' : 'bg-[#6D5DF6] dark:bg-[#6D5DF6]/20 text-[#6D5DF6] dark:text-[#A78BFA] hover:bg-[#6D5DF6] dark:bg-[#6D5DF6]/30'}`}>
                    {findingState === 'running' ? '⏸ Pause' : findingState === 'paused' ? '▶ Continue Finding' : '🔍 Find Websites'}
                    {findingState !== 'idle' && ` (${findingFoundCount}/${findingProcessedCount} / ${results.length})`}
                  </button>
                  <button onClick={toggleCrawlWebsites} disabled={findingState === 'running'}
                    className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${findingState === 'running' ? 'opacity-50 cursor-not-allowed bg-gray-500/20 text-gray-400' : crawlingState === 'running' ? 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30' : crawlingState === 'paused' ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30' : 'bg-accent-violet/20 text-[#A78BFA] hover:bg-accent-violet/30'}`}>
                    {crawlingState === 'running' ? '⏸ Pause' : crawlingState === 'paused' ? '▶ Continue Crawling' : '🕷 Crawl Websites'}
                    {crawlingState !== 'idle' && ` (${crawlingFoundCount}/${crawlingProcessedCount} / ${results.length})`}
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="bg-slate-100 dark:bg-white/[0.04] border-b border-slate-200/80 dark:border-white/[0.06]">
                    <tr>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Name</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Website</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Phone</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Email</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Facebook</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Instagram</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Address</th>
                      <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((biz, i) => (
                      <tr key={i} className={`border-b border-slate-200/80 dark:border-white/[0.06] hover:bg-slate-50 dark:hover:bg-white/[0.06] transition-colors ${i % 2 === 0 ? 'bg-slate-50 dark:bg-white/[0.02]' : 'bg-white dark:bg-white/[0.01]'}`}>
                        <td className="px-3 py-3">
                          <p className="font-medium text-slate-900 dark:text-white">{biz.business_name || biz.name || biz.display_name || '-'}</p>
                          <p className="text-xs text-slate-500 dark:text-[#8E8BA3]">{biz.category || ''}</p>
                        </td>
                        <td className="px-3 py-3">
                          {biz.website ? (
                            <div>
                              <a href={biz.website} target="_blank" rel="noopener noreferrer" className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] text-xs truncate max-w-[150px] block">{biz.website}</a>
                              {biz.source_website === 'directory' && <span className="text-[10px] text-emerald-400 block mt-0.5">found 🗺️</span>}
                            </div>
                          ) : '-'}
                        </td>
                        <td className="px-3 py-3 text-slate-500 dark:text-[#8E8BA3]">
                          {biz.phone ? (
                            <div>
                              <span className="text-xs">{biz.phone}</span>
                              {biz.source_phone === 'directory' && <span className="text-[10px] text-emerald-400 block mt-0.5">found 🗺️</span>}
                              {biz.source_phone === 'website' && <span className="text-[10px] text-[#6D5DF6] dark:text-[#A78BFA] block mt-0.5">found 🌐</span>}
                            </div>
                          ) : '-'}
                        </td>
                        <td className="px-3 py-3">
                          {biz.crawled_email ? (
                            <div>
                              <span className="text-[#8BA1C1] text-xs">{biz.crawled_email}</span>
                              {biz.source_email === 'directory' && <span className="text-[10px] text-emerald-400 block mt-0.5">found 🗺️</span>}
                              {biz.source_email === 'website' && <span className="text-[10px] text-[#6D5DF6] dark:text-[#A78BFA] block mt-0.5">found 🌐</span>}
                            </div>
                          ) : biz.website ? (
                            <button onClick={() => crawlForEmail(biz, i)} disabled={crawling[i]}
                              className="text-xs text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] font-medium">
                              {crawling[i] ? 'Crawling...' : '🔍 Find Email'}
                            </button>
                          ) : '-'}
                        </td>
                        <td className="px-3 py-3 text-slate-500 dark:text-[#8E8BA3]">
                          {biz.facebook ? (
                            <div>
                              <a href={biz.facebook} target="_blank" rel="noopener noreferrer" className="text-[#6D5DF6] dark:text-[#A78BFA] text-xs hover:underline">Link</a>
                              {biz.source_facebook === 'directory' && <span className="text-[10px] text-emerald-400 block mt-0.5">found 🗺️</span>}
                              {biz.source_facebook === 'website' && <span className="text-[10px] text-[#6D5DF6] dark:text-[#A78BFA] block mt-0.5">found 🌐</span>}
                            </div>
                          ) : '-'}
                        </td>
                        <td className="px-3 py-3 text-slate-500 dark:text-[#8E8BA3]">
                          {biz.instagram ? (
                            <div>
                              <a href={biz.instagram} target="_blank" rel="noopener noreferrer" className="text-[#6D5DF6] dark:text-[#A78BFA] text-xs hover:underline">Link</a>
                              {biz.source_instagram === 'directory' && <span className="text-[10px] text-emerald-400 block mt-0.5">found 🗺️</span>}
                              {biz.source_instagram === 'website' && <span className="text-[10px] text-[#6D5DF6] dark:text-[#A78BFA] block mt-0.5">found 🌐</span>}
                            </div>
                          ) : '-'}
                        </td>
                        <td className="px-3 py-3 text-slate-500 dark:text-[#8E8BA3] text-xs max-w-[200px] truncate">{biz.address || '-'}</td>
                        <td className="px-3 py-3">
                          <div className="flex space-x-2">
                            <button onClick={() => openSaveModal(biz)} className="text-xs font-medium text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA]">Save</button>
                            {biz.website && (
                              <button onClick={() => goToAudit(biz)} className="text-xs font-medium text-amber-500 hover:text-amber-400">Audit</button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Saved Businesses Tab */}
      {activeTab === 'saved' && (
        <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] shadow-sm dark:shadow-none">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Saved Businesses</h3>
          {bizLoading ? (
            <div className="text-center py-12 text-slate-500 dark:text-[#8E8BA3] flex items-center justify-center">
              <Spinner className="mr-2 h-5 w-5" /> Loading...
            </div>
          ) : businesses.length === 0 ? (
            <div className="text-center py-12 text-slate-500 dark:text-[#8E8BA3]">
              <p>No saved businesses yet.</p>
              <button onClick={() => setActiveTab('search')} className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] mt-2">Start hunting!</button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-100 dark:bg-white/[0.04] border-b border-slate-200/80 dark:border-white/[0.06]">
                  <tr>
                    <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Business</th>
                    <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Website</th>
                    <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Email</th>
                    <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Score</th>
                    <th className="px-3 py-3 font-semibold text-slate-400 dark:text-[#6B6890] uppercase tracking-wide text-xs">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {businesses.map((biz, i) => (
                    <tr key={biz.id} className={`border-b border-slate-200/80 dark:border-white/[0.06] hover:bg-slate-50 dark:hover:bg-white/[0.06] transition-colors ${i % 2 === 0 ? 'bg-slate-50 dark:bg-white/[0.02]' : 'bg-white dark:bg-white/[0.01]'}`}>
                      <td className="px-3 py-3">
                        <p className="font-medium text-slate-900 dark:text-white">{biz.business_name}</p>
                        <p className="text-xs text-slate-500 dark:text-[#8E8BA3]">{biz.city || ''}</p>
                      </td>
                      <td className="px-3 py-3">
                        {biz.website ? (
                          <a href={biz.website} target="_blank" rel="noopener noreferrer" className="text-[#6D5DF6] dark:text-[#A78BFA] hover:text-[#5b4ee4] dark:hover:text-[#A78BFA] text-xs truncate max-w-[150px] block">{biz.website}</a>
                        ) : '-'}
                      </td>
                      <td className="px-3 py-3 text-slate-500 dark:text-[#8E8BA3] text-xs">{biz.email || '-'}</td>
                      <td className="px-3 py-3">
                        {biz.audit_completed ? (
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium ${
                            biz.overall_score >= 4 ? 'bg-emerald-500/10 text-emerald-400' :
                            biz.overall_score >= 3 ? 'bg-amber-500/20 text-amber-400' :
                            'bg-red-500/10 text-red-400'
                          }`}>
                            {(biz.overall_score || 0).toFixed(1)}/5
                          </span>
                        ) : (
                          <span className="text-xs text-slate-500 dark:text-[#8E8BA3]">—</span>
                        )}
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex space-x-2">
                          {biz.website && (
                            <button onClick={() => goToAudit(biz)} className="text-xs font-medium text-amber-500 hover:text-amber-400">Audit</button>
                          )}
                          {biz.email && (
                            <button onClick={() => goToOutreach(biz)} className="text-xs font-medium text-[#A78BFA] hover:text-purple-400">Outreach</button>
                          )}
                          <button onClick={() => deleteBusiness(biz.id)} className="text-xs font-medium text-red-500 hover:text-red-400">Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Save Business Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-white/[0.015] rounded-xl p-6 border border-slate-200/80 dark:border-white/[0.06] w-full max-w-md shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Save Business</h3>
            <p className="text-sm text-slate-500 dark:text-[#8E8BA3] mb-4">{savingBusiness?.name || savingBusiness?.display_name}</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Email (optional)</label>
                <input value={saveForm.email} onChange={e => setSaveForm(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]"
                  placeholder="contact@example.com" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Phone</label>
                <input value={saveForm.phone} onChange={e => setSaveForm(prev => ({ ...prev, phone: e.target.value }))}
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]"
                  placeholder="+1 234 567 8900" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-500 dark:text-[#8E8BA3] mb-1.5">Notes</label>
                <textarea value={saveForm.notes} onChange={e => setSaveForm(prev => ({ ...prev, notes: e.target.value }))}
                  className="w-full px-4 py-2.5 bg-slate-100 dark:bg-[#08061a] border border-slate-200/80 dark:border-white/[0.06] rounded-lg text-slate-900 dark:text-white placeholder-text-muted focus:outline-none focus:border-[#6D5DF6] dark:focus:border-[#A78BFA]"
                  rows="3" placeholder="Any notes..." />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button onClick={() => setShowSaveModal(false)} className="px-4 py-2 text-sm text-slate-500 dark:text-[#8E8BA3] hover:text-slate-900 dark:text-white transition-colors">Cancel</button>
              <button onClick={saveBusiness} className="bg-[#6D5DF6] dark:bg-[#6D5DF6] hover:bg-[#5b4ee4] dark:hover:bg-[#5b4ee4] text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm">Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

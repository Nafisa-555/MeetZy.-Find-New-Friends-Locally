const { useState, useEffect, useRef } = React;

// ============================================
// API Configuration — DO NOT CHANGE
// ============================================
const API_BASE_URL = window.location.origin;

const api = {
    parseError: async (response) => {
        try {
            const error = await response.json();
            if (error.detail) {
                if (typeof error.detail === 'string') return error.detail;
                if (Array.isArray(error.detail)) return error.detail.map(e => e.msg).join(', ');
            }
            return error.message || 'An error occurred';
        } catch (e) {
            return `Error ${response.status}: ${response.statusText}`;
        }
    },
    signup: async (data) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    login: async (data) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getCurrentUser: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getProfile: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/users/profile`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    updateProfile: async (token, data) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/users/profile`, {
            method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    updateInterests: async (token, interestIds) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/users/interests`, {
            method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ interest_ids: interestIds })
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getAvailableInterests: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/users/interests/available`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    updateLocation: async (token, latitude, longitude) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/users/location`, {
            method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude })
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    findMatches: async (token, maxDistance = 50, minMatch = 30, limit = 20) => {
        const r = await fetch(
            `${API_BASE_URL}/api/v1/matches/find-friends?max_distance_km=${maxDistance}&min_match_percentage=${minMatch}&limit=${limit}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
        );
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getMatchPreview: async (token, userId) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/matches/preview/${userId}`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    sendFriendRequest: async (token, receiverId) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/friends/request`, {
            method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ receiver_id: receiverId })
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getPendingRequests: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/friends/requests/pending`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    acceptFriendRequest: async (token, requestId) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/friends/request/${requestId}/accept`, {
            method: 'PUT', headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    rejectFriendRequest: async (token, requestId) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/friends/request/${requestId}/reject`, {
            method: 'PUT', headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getFriendsList: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/friends/`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    unfriend: async (token, friendId) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/friends/${friendId}`, {
            method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r;
    },
    sendMessage: async (token, receiverId, content) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/chat/messages/${receiverId}`, {
            method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getConversation: async (token, friendId, limit = 50) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/chat/messages/${friendId}?limit=${limit}`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    markMessagesRead: async (token, messageIds) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/chat/messages/read`, {
            method: 'PUT', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ message_ids: messageIds })
        });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getConversationsList: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/chat/conversations`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    },
    getUnreadCount: async (token) => {
        const r = await fetch(`${API_BASE_URL}/api/v1/chat/unread-count`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!r.ok) throw new Error(await api.parseError(r));
        return r.json();
    }
};

// ============================================
// Utility Components
// ============================================

function Avatar({ name, size = 'md' }) {
    const initials = (name || '?').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    const colors = [
        'linear-gradient(135deg, #B66BFF 0%, #9B45F0 100%)',
        'linear-gradient(135deg, #4ECDC4 0%, #2BA9A0 100%)',
        'linear-gradient(135deg, #FF6B6B 0%, #E84040 100%)',
        'linear-gradient(135deg, #FFD166 0%, #F0A500 100%)',
        'linear-gradient(135deg, #06D6A0 0%, #048A64 100%)',
    ];
    const colorIdx = (name || '').charCodeAt(0) % colors.length;
    return (
        <div className={`avatar avatar-${size}`} style={{ background: colors[colorIdx] }}>
            {initials}
        </div>
    );
}

function Spinner({ small }) {
    return <div className={`spinner${small ? ' spinner-sm' : ''}`}></div>;
}

function LoadingScreen({ text }) {
    return (
        <div className="loading-screen">
            <Spinner />
            {text && <p>{text}</p>}
        </div>
    );
}

// ============================================
// Auth Component
// ============================================

function Auth({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({ email: '', password: '', name: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        if (!isLogin) {
            if (formData.password.length < 8) { setError('Password must be at least 8 characters long'); setLoading(false); return; }
            if (formData.name.length < 2) { setError('Name must be at least 2 characters long'); setLoading(false); return; }
        }
        try {
            let response;
            if (isLogin) {
                response = await api.login({ email: formData.email, password: formData.password });
            } else {
                response = await api.signup({ email: formData.email, password: formData.password, name: formData.name });
            }
            localStorage.setItem('token', response.access_token);
            onLogin(response.access_token);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const switchMode = (loginMode) => {
        setIsLogin(loginMode);
        setError('');
        setFormData({ email: '', password: '', name: '' });
    };

    return (
        <div className="auth-page">
            <div className="auth-bg-blob auth-bg-blob-1"></div>
            <div className="auth-bg-blob auth-bg-blob-2"></div>
            <div className="auth-card">
                <div className="auth-header">
                    <span className="auth-logo">MeetZy</span>
                    <p className="auth-tagline">Find friends based on shared interests</p>
                </div>

                <div className="auth-tabs">
                    <button className={`auth-tab${isLogin ? ' active' : ''}`} onClick={() => switchMode(true)}>Login</button>
                    <button className={`auth-tab${!isLogin ? ' active' : ''}`} onClick={() => switchMode(false)}>Sign Up</button>
                </div>

                {error && (
                    <div className="alert alert-error mb-4">
                        <span>⚠</span> {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {!isLogin && (
                        <div>
                            <label className="input-label">Name</label>
                            <input type="text" className="input-field" placeholder="Your full name" value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })} required minLength={2} />
                            <p className="input-hint">At least 2 characters</p>
                        </div>
                    )}
                    <div>
                        <label className="input-label">Email</label>
                        <input type="email" className="input-field" placeholder="you@example.com" value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
                    </div>
                    <div>
                        <label className="input-label">Password</label>
                        <input type="password" className="input-field" placeholder="••••••••" value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })} required minLength={isLogin ? undefined : 8} />
                        {!isLogin && <p className="input-hint">At least 8 characters</p>}
                    </div>
                    <button type="submit" className="btn btn-primary btn-full" disabled={loading} style={{ marginTop: '8px' }}>
                        {loading ? <Spinner small /> : (isLogin ? 'Sign In →' : 'Create Account →')}
                    </button>
                </form>
            </div>
        </div>
    );
}

// ============================================
// Profile Component
// ============================================

function Profile({ token, user }) {
    const [profile, setProfile] = useState(null);
    const [availableInterests, setAvailableInterests] = useState({});
    const [selectedInterests, setSelectedInterests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingInterests, setLoadingInterests] = useState(true);
    const [interestsError, setInterestsError] = useState(false);
    const [editing, setEditing] = useState(false);
    const [updatingInterests, setUpdatingInterests] = useState(false);
    const [updatingProfile, setUpdatingProfile] = useState(false);
    const [profileMsg, setProfileMsg] = useState(null);
    const [interestsMsg, setInterestsMsg] = useState(null);
    const [formData, setFormData] = useState({ name: '', bio: '', latitude: '', longitude: '' });

    useEffect(() => { loadProfile(); loadInterests(); }, []);

    const loadProfile = async () => {
        try {
            const data = await api.getProfile(token);
            setProfile(data);
            setFormData({ name: data.name || '', bio: data.bio || '', latitude: data.latitude || '', longitude: data.longitude || '' });
            setSelectedInterests(data.interests.map(i => i.id));
            setLoading(false);
        } catch (err) {
            setProfileMsg({ type: 'error', text: 'Failed to load profile: ' + err.message });
            setLoading(false);
        }
    };

    const loadInterests = async () => {
        setLoadingInterests(true);
        setInterestsError(false);
        try {
            const data = await api.getAvailableInterests(token);
            if (!data || Object.keys(data).length === 0) { setInterestsError(true); setAvailableInterests({}); }
            else setAvailableInterests(data);
        } catch (err) {
            setInterestsError(true);
            setAvailableInterests({});
        } finally {
            setLoadingInterests(false);
        }
    };

    const handleGetLocation = () => {
        if (!navigator.geolocation) { alert('Geolocation not supported'); return; }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setFormData({ ...formData, latitude: pos.coords.latitude.toString(), longitude: pos.coords.longitude.toString() });
                setProfileMsg({ type: 'success', text: `Location set: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}` });
            },
            (err) => {
                const msgs = { 1: 'Location permission denied.', 2: 'Location unavailable.', 3: 'Location request timed out.' };
                setProfileMsg({ type: 'error', text: msgs[err.code] || 'Unknown error getting location.' });
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setUpdatingProfile(true);
        setProfileMsg(null);
        try {
            const updateData = {};
            if (formData.name && formData.name.trim()) updateData.name = formData.name.trim();
            if (formData.bio !== null && formData.bio !== undefined) updateData.bio = formData.bio.trim();
            if (formData.latitude) updateData.latitude = parseFloat(formData.latitude);
            if (formData.longitude) updateData.longitude = parseFloat(formData.longitude);
            await api.updateProfile(token, updateData);
            await loadProfile();
            setEditing(false);
            setProfileMsg({ type: 'success', text: '✓ Profile updated successfully!' });
        } catch (err) {
            setProfileMsg({ type: 'error', text: 'Failed to update: ' + err.message });
        } finally {
            setUpdatingProfile(false);
        }
    };

    const handleUpdateInterests = async () => {
        if (selectedInterests.length < 1 || selectedInterests.length > 10) {
            setInterestsMsg({ type: 'error', text: 'Select between 1 and 10 interests' });
            return;
        }
        setUpdatingInterests(true);
        setInterestsMsg(null);
        try {
            await api.updateInterests(token, selectedInterests);
            await loadProfile();
            setInterestsMsg({ type: 'success', text: '✓ Interests updated successfully!' });
        } catch (err) {
            setInterestsMsg({ type: 'error', text: 'Failed to update interests: ' + err.message });
        } finally {
            setUpdatingInterests(false);
        }
    };

    const toggleInterest = (id) => {
        if (selectedInterests.includes(id)) {
            setSelectedInterests(selectedInterests.filter(i => i !== id));
        } else {
            if (selectedInterests.length >= 10) { setInterestsMsg({ type: 'error', text: 'Maximum 10 interests allowed' }); return; }
            setSelectedInterests([...selectedInterests, id]);
        }
    };

    if (loading) return <LoadingScreen text="Loading your profile..." />;

    return (
        <div className="page-section fade-up">
            {/* Profile Card */}
            <div className="card mb-4">
                <div className="profile-hero">
                    <Avatar name={profile.name} size="xl" />
                    <div className="profile-info">
                        <div className="profile-name">{profile.name}</div>
                        <div className="profile-email">{profile.email}</div>
                        <div className="profile-stats">
                            <span className="profile-stat">👥 {profile.friend_count} friends</span>
                            {profile.interests && <span className="profile-stat">✨ {profile.interests.length} interests</span>}
                            {profile.latitude && profile.longitude && (
                                <span className="profile-stat">📍 Location set</span>
                            )}
                        </div>
                    </div>
                    <button onClick={() => { setEditing(!editing); setProfileMsg(null); }} className={`btn btn-sm profile-edit-btn ${editing ? 'btn-secondary' : 'btn-ghost'}`}>
                        {editing ? '✕ Cancel' : '✏️ Edit'}
                    </button>
                </div>

                {profileMsg && (
                    <div style={{ padding: '0 28px 16px' }}>
                        <div className={`alert alert-${profileMsg.type}`}>{profileMsg.text}</div>
                    </div>
                )}

                {editing ? (
                    <form onSubmit={handleUpdateProfile} style={{ padding: '0 28px 28px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div className="divider mb-4"></div>
                        <div>
                            <label className="input-label">Name</label>
                            <input type="text" className="input-field" value={formData.name} placeholder="Your name"
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
                        </div>
                        <div>
                            <label className="input-label">Bio</label>
                            <textarea className="input-field" rows="3" value={formData.bio} placeholder="Tell us about yourself..."
                                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                                style={{ resize: 'vertical', minHeight: '80px' }} />
                            <p className="input-hint">Max 500 characters</p>
                        </div>
                        <div>
                            <label className="input-label">Location</label>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '10px' }}>
                                <div>
                                    <input type="number" step="any" className="input-field" value={formData.latitude} placeholder="Latitude"
                                        onChange={(e) => setFormData({ ...formData, latitude: e.target.value })} />
                                    <p className="input-hint">-90 to 90</p>
                                </div>
                                <div>
                                    <input type="number" step="any" className="input-field" value={formData.longitude} placeholder="Longitude"
                                        onChange={(e) => setFormData({ ...formData, longitude: e.target.value })} />
                                    <p className="input-hint">-180 to 180</p>
                                </div>
                            </div>
                            <button type="button" onClick={handleGetLocation} className="btn btn-secondary btn-sm">
                                📍 Detect My Location
                            </button>
                        </div>
                        <button type="submit" className="btn btn-primary" disabled={updatingProfile} style={{ alignSelf: 'flex-start', minWidth: '160px' }}>
                            {updatingProfile ? <><Spinner small /> Saving...</> : 'Save Changes'}
                        </button>
                    </form>
                ) : (
                    <div className="profile-section">
                        {(profile.bio || (profile.latitude && profile.longitude)) && <div className="divider mb-4"></div>}
                        {profile.bio && (
                            <div style={{ marginBottom: '12px' }}>
                                <div className="profile-section-title">About</div>
                                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>{profile.bio}</p>
                            </div>
                        )}
                        {profile.latitude && profile.longitude && (
                            <div>
                                <div className="profile-section-title">Location</div>
                                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                                    📍 {profile.latitude.toFixed(4)}, {profile.longitude.toFixed(4)}
                                </p>
                            </div>
                        )}
                        {!profile.bio && !profile.latitude && (
                            <p style={{ fontSize: '14px', color: 'var(--text-muted)', paddingBottom: '8px' }}>
                                No profile details yet. Click Edit to add your bio and location.
                            </p>
                        )}
                    </div>
                )}
            </div>

            {/* Interests Card */}
            <div className="card interests-card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: '700' }}>Your Interests</h2>
                </div>

                {profile.interests.length > 0 && (
                    <div className="interests-row mb-4">
                        {profile.interests.map(interest => (
                            <span key={interest.id} className="interest-tag">{interest.icon} {interest.name}</span>
                        ))}
                    </div>
                )}

                <div className="divider mb-4"></div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Select Interests</h3>
                    <span style={{ fontSize: '13px', color: selectedInterests.length > 10 ? 'var(--danger)' : 'var(--primary)', fontWeight: '700' }}>
                        {selectedInterests.length}/10
                    </span>
                </div>

                {interestsMsg && (
                    <div className={`alert alert-${interestsMsg.type} mb-4`}>{interestsMsg.text}</div>
                )}

                {loadingInterests ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
                        <Spinner />
                    </div>
                ) : interestsError || Object.entries(availableInterests).length === 0 ? (
                    <div className="no-interests-box">
                        <div style={{ fontSize: '32px', marginBottom: '8px' }}>⚠️</div>
                        <h4>No Interests Available</h4>
                        <p>The database doesn't have any interests yet. Populate it first:</p>
                        <div className="code-block">python populate_interests.py</div>
                        <button onClick={loadInterests} className="btn btn-primary btn-sm mt-2">🔄 Retry</button>
                    </div>
                ) : (
                    <>
                        {Object.entries(availableInterests).map(([category, interests]) => (
                            <div key={category} className="category-section">
                                <div className="category-title">{category}</div>
                                <div className="interests-row">
                                    {interests.map(interest => (
                                        <button key={interest.id} type="button"
                                            className={`interest-tag selectable${selectedInterests.includes(interest.id) ? ' selected' : ''}`}
                                            onClick={() => toggleInterest(interest.id)}>
                                            {interest.icon} {interest.name}
                                            {selectedInterests.includes(interest.id) && ' ✓'}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ))}
                        <button onClick={handleUpdateInterests} className="btn btn-primary mt-3"
                            disabled={selectedInterests.length < 1 || selectedInterests.length > 10 || updatingInterests}
                            style={{ minWidth: '200px' }}>
                            {updatingInterests ? <><Spinner small /> Updating...</> : `Save Interests (${selectedInterests.length} selected)`}
                        </button>
                        {selectedInterests.length > 10 && <p style={{ fontSize: '12px', color: 'var(--danger)', marginTop: '6px' }}>⚠️ Select up to 10 interests</p>}
                        {selectedInterests.length < 1 && <p style={{ fontSize: '12px', color: 'var(--accent)', marginTop: '6px' }}>⚠️ Select at least 1 interest</p>}
                    </>
                )}
            </div>
        </div>
    );
}

// ============================================
// Find Matches Component
// ============================================

function FindMatches({ token }) {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [sendingTo, setSendingTo] = useState(null);
    const [filters, setFilters] = useState({ maxDistance: 50, minMatch: 30, limit: 20 });

    useEffect(() => { loadMatches(); }, []);

    const loadMatches = async () => {
        setLoading(true);
        try {
            const data = await api.findMatches(token, filters.maxDistance, filters.minMatch, filters.limit);
            setMatches(data.matches);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleSendRequest = async (userId) => {
        setSendingTo(userId);
        try {
            await api.sendFriendRequest(token, userId);
            setMatches(matches.filter(m => m.id !== userId));
        } catch (err) {
            alert(err.message);
        } finally {
            setSendingTo(null);
        }
    };

    return (
        <div className="page-section">
            <div className="page-header">
                <h1 className="page-title">Find Friends</h1>
                <p className="page-subtitle">Discover people with shared interests near you</p>
            </div>

            {/* Filters */}
            <div className="card filters-card fade-up">
                <h2 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>🎛️ Filters</h2>
                <div className="filters-grid">
                    <div className="filter-item">
                        <label>
                            Max Distance
                            <span className="filter-value">{filters.maxDistance} km</span>
                        </label>
                        <input type="range" min="1" max="200" value={filters.maxDistance}
                            onChange={(e) => setFilters({ ...filters, maxDistance: e.target.value })} />
                    </div>
                    <div className="filter-item">
                        <label>
                            Min Match
                            <span className="filter-value">{filters.minMatch}%</span>
                        </label>
                        <input type="range" min="0" max="100" value={filters.minMatch}
                            onChange={(e) => setFilters({ ...filters, minMatch: e.target.value })} />
                    </div>
                    <div className="filter-item">
                        <label>
                            Results
                            <span className="filter-value">{filters.limit}</span>
                        </label>
                        <input type="range" min="5" max="50" value={filters.limit}
                            onChange={(e) => setFilters({ ...filters, limit: e.target.value })} />
                    </div>
                </div>
                <button onClick={loadMatches} className="btn btn-primary btn-sm" disabled={loading}>
                    {loading ? <><Spinner small /> Searching...</> : '🔍 Apply Filters'}
                </button>
            </div>

            {loading ? (
                <LoadingScreen text="Finding your matches..." />
            ) : matches.length === 0 ? (
                <div className="card fade-in">
                    <div className="empty-state">
                        <div className="empty-icon">🔍</div>
                        <div className="empty-title">No matches found</div>
                        <p className="empty-text">Try adjusting your filters or adding more interests to your profile.</p>
                    </div>
                </div>
            ) : (
                <div className="matches-grid stagger">
                    {matches.map((match) => (
                        <div key={match.id} className="card card-hover match-card fade-up">
                            <div className="match-card-header">
                                <div className="match-card-user">
                                    <Avatar name={match.name} size="md" />
                                    <div className="match-card-info">
                                        <div className="match-card-name">{match.name}</div>
                                        {match.distance_km && (
                                            <div className="match-card-distance">📍 {match.distance_km.toFixed(1)} km away</div>
                                        )}
                                    </div>
                                </div>
                                <div className="match-badge">⚡ {match.match_percentage}%</div>
                            </div>

                            {match.bio && <p className="match-card-bio">{match.bio}</p>}

                            {match.common_interests && match.common_interests.length > 0 && (
                                <div>
                                    <div className="match-interests-label">Common Interests</div>
                                    <div className="match-interests">
                                        {match.common_interests.slice(0, 5).map((interest, idx) => (
                                            <span key={idx} className="interest-tag" style={{ fontSize: '11px', padding: '3px 10px' }}>{interest}</span>
                                        ))}
                                        {match.common_interests.length > 5 && (
                                            <span style={{ fontSize: '11px', color: 'var(--text-muted)', alignSelf: 'center' }}>+{match.common_interests.length - 5} more</span>
                                        )}
                                    </div>
                                </div>
                            )}

                            <button onClick={() => handleSendRequest(match.id)} className="btn btn-primary btn-full btn-sm"
                                disabled={sendingTo === match.id}>
                                {sendingTo === match.id ? <><Spinner small /> Sending...</> : '➕ Send Friend Request'}
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// ============================================
// Friends Component
// ============================================

function Friends({ token }) {
    const [friends, setFriends] = useState([]);
    const [pendingRequests, setPendingRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('friends');

    useEffect(() => { loadFriends(); loadPendingRequests(); }, []);

    const loadFriends = async () => {
        try {
            const data = await api.getFriendsList(token);
            setFriends(data.friends);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const loadPendingRequests = async () => {
        try {
            const data = await api.getPendingRequests(token);
            setPendingRequests(data);
        } catch (err) { console.error(err); }
    };

    const handleAcceptRequest = async (requestId) => {
        try {
            await api.acceptFriendRequest(token, requestId);
            loadPendingRequests();
            loadFriends();
        } catch (err) { alert(err.message); }
    };

    const handleRejectRequest = async (requestId) => {
        try {
            await api.rejectFriendRequest(token, requestId);
            loadPendingRequests();
        } catch (err) { alert(err.message); }
    };

    const handleUnfriend = async (friendId) => {
        if (!confirm('Are you sure you want to unfriend this person?')) return;
        try {
            await api.unfriend(token, friendId);
            loadFriends();
        } catch (err) { alert(err.message); }
    };

    if (loading) return <LoadingScreen text="Loading friends..." />;

    return (
        <div className="page-section">
            <div className="page-header">
                <h1 className="page-title">Friends</h1>
                <p className="page-subtitle">Manage your connections</p>
            </div>

            <div className="friends-tabs">
                <button className={`tab-btn${activeTab === 'friends' ? ' active' : ''}`} onClick={() => setActiveTab('friends')}>
                    👥 My Friends <span className="tab-count">{friends.length}</span>
                </button>
                <button className={`tab-btn${activeTab === 'requests' ? ' active' : ''}`} onClick={() => setActiveTab('requests')}>
                    🔔 Requests <span className="tab-count">{pendingRequests.length}</span>
                </button>
            </div>

            {activeTab === 'friends' ? (
                friends.length === 0 ? (
                    <div className="card fade-in">
                        <div className="empty-state">
                            <div className="empty-icon">👥</div>
                            <div className="empty-title">No friends yet</div>
                            <p className="empty-text">Start finding matches and send friend requests!</p>
                        </div>
                    </div>
                ) : (
                    <div className="matches-grid stagger">
                        {friends.map((friend) => (
                            <div key={friend.id} className="card card-hover match-card fade-up">
                                <div className="match-card-user">
                                    <Avatar name={friend.name} size="md" />
                                    <div className="match-card-info">
                                        <div className="match-card-name">{friend.name}</div>
                                        {friend.common_interests_count > 0 && (
                                            <div className="match-card-distance">✨ {friend.common_interests_count} common interests</div>
                                        )}
                                    </div>
                                </div>
                                {friend.bio && <p className="match-card-bio">{friend.bio}</p>}
                                <button onClick={() => handleUnfriend(friend.id)} className="btn btn-danger btn-sm btn-full">
                                    Unfriend
                                </button>
                            </div>
                        ))}
                    </div>
                )
            ) : (
                pendingRequests.length === 0 ? (
                    <div className="card fade-in">
                        <div className="empty-state">
                            <div className="empty-icon">🔔</div>
                            <div className="empty-title">No pending requests</div>
                            <p className="empty-text">You're all caught up!</p>
                        </div>
                    </div>
                ) : (
                    <div className="matches-grid stagger">
                        {pendingRequests.map((request) => (
                            <div key={request.id} className="card match-card fade-up">
                                <div className="match-card-user">
                                    <Avatar name={request.sender_name} size="md" />
                                    <div className="match-card-info">
                                        <div className="match-card-name">{request.sender_name}</div>
                                        <div className="match-card-distance">{new Date(request.created_at).toLocaleDateString()}</div>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button onClick={() => handleAcceptRequest(request.id)} className="btn btn-primary btn-sm flex-1">✓ Accept</button>
                                    <button onClick={() => handleRejectRequest(request.id)} className="btn btn-secondary btn-sm flex-1">✕ Reject</button>
                                </div>
                            </div>
                        ))}
                    </div>
                )
            )}
        </div>
    );
}

// ============================================
// Chat Component
// ============================================

function Chat({ token, currentUserId }) {
    const [friends, setFriends] = useState([]);
    const [selectedFriend, setSelectedFriend] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [showChat, setShowChat] = useState(false); // mobile: true = show chat panel
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const isMobile = () => window.innerWidth <= 768;

    useEffect(() => { loadFriends(); }, []);

    useEffect(() => {
        if (selectedFriend) {
            loadConversation(selectedFriend.id);
            if (isMobile()) setShowChat(true);
        }
    }, [selectedFriend]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadFriends = async () => {
        try {
            const data = await api.getFriendsList(token);
            setFriends(data.friends);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const loadConversation = async (friendId) => {
        try {
            const data = await api.getConversation(token, friendId);
            setMessages(data.messages);
        } catch (err) { console.error(err); }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !selectedFriend) return;
        const content = newMessage;
        setNewMessage('');
        try {
            const message = await api.sendMessage(token, selectedFriend.id, content);
            setMessages(prev => [...prev, message]);
        } catch (err) {
            alert(err.message);
            setNewMessage(content);
        }
    };

    const handleBack = () => {
        setShowChat(false);
        setSelectedFriend(null);
    };

    if (loading) return <LoadingScreen text="Loading messages..." />;

    // On mobile: show sidebar OR chat, not both
    const sidebarVisible = !isMobile() || !showChat;
    const chatVisible = !isMobile() || showChat;

    return (
        <div className="chat-container">
            <div className="chat-card">
                {/* Sidebar */}
                <div className={`chat-sidebar${sidebarVisible ? '' : ' hidden'}`}>
                    <div className="chat-sidebar-header">
                        <h2>Messages</h2>
                    </div>
                    <div className="chat-friend-list">
                        {friends.length === 0 ? (
                            <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                                No friends to chat with yet
                            </div>
                        ) : (
                            friends.map((friend) => (
                                <div key={friend.id} onClick={() => setSelectedFriend(friend)}
                                    className={`chat-friend-item${selectedFriend?.id === friend.id ? ' active' : ''}`}>
                                    <Avatar name={friend.name} size="sm" />
                                    <div className="chat-friend-info">
                                        <div className="chat-friend-name">{friend.name}</div>
                                        {friend.bio && <div className="chat-friend-bio">{friend.bio}</div>}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Chat Area */}
                <div className={`chat-main${chatVisible ? '' : ' hidden'}`}>
                    {selectedFriend ? (
                        <>
                            <div className="chat-header">
                                <button className="chat-back-btn" onClick={handleBack}>←</button>
                                <Avatar name={selectedFriend.name} size="sm" />
                                <div className="chat-header-info">
                                    <div className="chat-header-name">{selectedFriend.name}</div>
                                    {selectedFriend.bio && <div className="chat-header-bio">{selectedFriend.bio}</div>}
                                </div>
                            </div>
                            <div className="chat-messages">
                                {messages.length === 0 ? (
                                    <div className="chat-empty">
                                        <div className="chat-empty-icon">💬</div>
                                        <div className="chat-empty-text">No messages yet. Say hello!</div>
                                    </div>
                                ) : (
                                    messages.map((msg) => (
                                        <div key={msg.id} className={`message-row ${msg.sender_id === currentUserId ? 'sent' : 'received'}`}>
                                            <div className={`message-bubble ${msg.sender_id === currentUserId ? 'sent' : 'received'}`}>
                                                <p>{msg.content}</p>
                                                <p className="message-time">{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                                            </div>
                                        </div>
                                    ))
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                            <form onSubmit={handleSendMessage} className="chat-input-area">
                                <input ref={inputRef} type="text" className="chat-input" placeholder="Type a message..."
                                    value={newMessage} onChange={(e) => setNewMessage(e.target.value)} />
                                <button type="submit" className="chat-send-btn" disabled={!newMessage.trim()}>➤</button>
                            </form>
                        </>
                    ) : (
                        <div className="chat-empty" style={{ flex: 1, display: 'flex' }}>
                            <div className="chat-empty-icon">💬</div>
                            <div className="chat-empty-text">Select a friend to start chatting</div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// ============================================
// Main App Component
// ============================================

function App() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [currentUser, setCurrentUser] = useState(null);
    const [currentPage, setCurrentPage] = useState('matches');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) loadCurrentUser();
        else setLoading(false);
    }, [token]);

    const loadCurrentUser = async () => {
        try {
            const user = await api.getCurrentUser(token);
            setCurrentUser(user);
            setLoading(false);
        } catch (err) {
            localStorage.removeItem('token');
            setToken(null);
            setLoading(false);
        }
    };

    const handleLogin = (newToken) => setToken(newToken);

    const handleLogout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setCurrentUser(null);
    };

    if (loading) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                    <Spinner />
                    <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Loading MeetZy...</span>
                </div>
            </div>
        );
    }

    if (!token) return <Auth onLogin={handleLogin} />;

    const navItems = [
        { id: 'matches', icon: '🔍', label: 'Discover' },
        { id: 'friends', icon: '👥', label: 'Friends' },
        { id: 'chat', icon: '💬', label: 'Chat' },
        { id: 'profile', icon: '👤', label: 'Profile' },
    ];

    return (
        <div className="app-container">
            {/* Desktop Nav */}
            <nav className="nav">
                <div className="nav-inner">
                    <div className="nav-logo">MeetZy</div>
                    <div className="nav-links">
                        {navItems.map(item => (
                            <button key={item.id} onClick={() => setCurrentPage(item.id)}
                                className={`nav-item${currentPage === item.id ? ' active' : ''}`}>
                                <span className="nav-icon">{item.icon}</span>
                                {item.label}
                            </button>
                        ))}
                    </div>
                    <div className="nav-right">
                        <div className="nav-user">
                            <Avatar name={currentUser?.name} size="sm" />
                            <span className="nav-user-name">{currentUser?.name}</span>
                        </div>
                        <button onClick={handleLogout} className="btn btn-secondary btn-sm">Logout</button>
                    </div>
                </div>
            </nav>

            {/* Mobile Top Bar */}
            <div className="mobile-topbar">
                <span className="mobile-topbar-logo">MeetZy</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Avatar name={currentUser?.name} size="sm" />
                    <button onClick={handleLogout} className="btn btn-secondary btn-sm">Out</button>
                </div>
            </div>

            {/* Page Content */}
            <div className="page-content">
                {currentPage === 'matches' && <FindMatches token={token} />}
                {currentPage === 'friends' && <Friends token={token} />}
                {currentPage === 'chat' && <Chat token={token} currentUserId={currentUser?.id} />}
                {currentPage === 'profile' && <Profile token={token} user={currentUser} />}
            </div>

            {/* Footer (desktop) */}
            <footer className="footer" style={{ display: 'none' }}>
                <p>© 2026 MeetZy</p>
                <p style={{ marginTop: '4px' }}>API: <code>{API_BASE_URL}</code></p>
            </footer>

            {/* Mobile Bottom Nav */}
            <nav className="mobile-nav">
                <div className="mobile-nav-inner">
                    {navItems.map(item => (
                        <button key={item.id} onClick={() => setCurrentPage(item.id)}
                            className={`mobile-nav-item${currentPage === item.id ? ' active' : ''}`}>
                            <span className="mn-icon">{item.icon}</span>
                            <span className="mn-label">{item.label}</span>
                        </button>
                    ))}
                </div>
            </nav>
        </div>
    );
}

// Render
ReactDOM.render(<App />, document.getElementById('root'));

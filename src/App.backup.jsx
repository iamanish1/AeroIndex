import { useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  CalendarDays,
  CircleDollarSign,
  Clock3,
  Plane,
  Search,
  Sparkles,
  TrendingDown,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const chartData = {
  Weekly: [
    { name: "Mon", avg: 8200, low: 6800 },
    { name: "Tue", avg: 7600, low: 6200 },
    { name: "Wed", avg: 8900, low: 7100 },
    { name: "Thu", avg: 7200, low: 5900 },
    { name: "Fri", avg: 9400, low: 7600 },
    { name: "Sat", avg: 8600, low: 6900 },
    { name: "Sun", avg: 7900, low: 6400 },
  ],
  Monthly: [
    { name: "Week 1", avg: 8200, low: 6800 },
    { name: "Week 2", avg: 7600, low: 6100 },
    { name: "Week 3", avg: 9100, low: 7300 },
    { name: "Week 4", avg: 7900, low: 6500 },
  ],
  Yearly: [
    { name: "Jan", avg: 7800, low: 6200 },
    { name: "Mar", avg: 8500, low: 6800 },
    { name: "May", avg: 9200, low: 7400 },
    { name: "Jul", avg: 10800, low: 8900 },
    { name: "Sep", avg: 8600, low: 6900 },
    { name: "Nov", avg: 8200, low: 6500 },
  ],
};

const getAirfareData = async (from, to) => {
  const response = await fetch(
    `http://127.0.0.1:5000/api/airfare?from=${encodeURIComponent(
      from
    )}&to=${encodeURIComponent(to)}`
  );

  if (!response.ok) {
    throw new Error("Unable to fetch airfare data");
  }

  return response.json();
};

function formatCurrency(value) {
  if (typeof value !== "number") {
    return "--";
  }

  return `₹${value.toLocaleString("en-IN")}`;
}

function formatAirlineData(airline) {
  const fare = Number(airline.fare || 0);

  return {
    name: airline.name,
    code:
      airline.name === "IndiGo"
        ? "6E"
        : airline.name === "Air India"
        ? "AI"
        : airline.name === "Vistara"
        ? "UK"
        : airline.name === "SpiceJet"
        ? "SG"
        : airline.name.slice(0, 2).toUpperCase(),
    price: formatCurrency(fare),
    avg: formatCurrency(Math.round(fare * 1.08)),
    diff: airline.change || "--",
  };
}

function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const [period, setPeriod] = useState("Monthly");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [error, setError] = useState("");
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  const cleanFrom = from.trim();
  const cleanTo = to.trim();

  const handleGetIndex = async () => {
    if (!cleanFrom || !cleanTo) {
      setError("Please enter both departure and arrival cities.");
      return;
    }

    if (cleanFrom.toLowerCase() === cleanTo.toLowerCase()) {
      setError("Departure and arrival cities cannot be the same.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const data = await getAirfareData(cleanFrom, cleanTo);

      setRouteData(data);
      setShowDashboard(true);
    } catch (err) {
      setError(
        "Backend se data nahi aa raha. Check karo Flask server running hai ya nahi."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEditRoute = () => {
    setShowDashboard(false);
    setError("");
  };

  const dashboardAirlines = (routeData?.airlines || []).map(
    formatAirlineData
  );

  const indexValue = routeData?.index ?? 0;
  const progressWidth = Math.min(Math.max(indexValue, 0), 100);

  return (
    <main className="app">
      <div className="background-glow glow-one" />
      <div className="background-glow glow-two" />

      <nav className="navbar">
        <div className="brand">
          <div className="brand-mark">
            <Plane size={21} strokeWidth={2.5} />
          </div>

          <span>
            Aero<span>Index</span>
          </span>
        </div>

        <div className="nav-links">
          <a href="#dashboard">Dashboard</a>
          <a href="#how-it-works">How it works</a>

          <button
            className="nav-login"
            onClick={() => setShowDashboard(false)}
          >
            Explore index
            <ArrowUpRight size={16} />
          </button>
        </div>
      </nav>

      {!showDashboard ? (
        <section className="hero-section">
          <div className="hero-copy">
            <div className="eyebrow">
              <Sparkles size={15} />
              <span>SMART AIRFARE INTELLIGENCE</span>
            </div>

            <h1>
              Know the price.
              <br />
              <span>Choose the flight.</span>
            </h1>

            <p className="hero-description">
              Compare airfare across airlines, understand price differences,
              and find the right time to fly.
            </p>

            <div className="search-card">
              <div className="search-field">
                <div className="field-icon">
                  <Plane size={18} />
                </div>

                <div>
                  <label>FROM</label>

                  <input
                    value={from}
                    onChange={(e) => {
                      setFrom(e.target.value);
                      setError("");
                    }}
                    placeholder="e.g. Delhi"
                  />
                </div>
              </div>

              <div className="route-divider">
                <ArrowRight size={18} />
              </div>

              <div className="search-field">
                <div className="field-icon">
                  <Plane size={18} />
                </div>

                <div>
                  <label>TO</label>

                  <input
                    value={to}
                    onChange={(e) => {
                      setTo(e.target.value);
                      setError("");
                    }}
                    placeholder="e.g. Mumbai"
                  />
                </div>
              </div>

              <button
                className="get-index-btn"
                onClick={handleGetIndex}
                disabled={loading}
              >
                {loading ? "Loading..." : "Get Index"}
                <ArrowRight size={18} />
              </button>
            </div>

            {error && (
              <p
                style={{
                  marginTop: "12px",
                  color: "#c2410c",
                  fontSize: "13px",
                }}
              >
                {error}
              </p>
            )}

            <div className="hero-trust">
              <div className="trust-item">
                <CircleDollarSign size={17} />
                <span>Compare smarter</span>
              </div>

              <div className="trust-item">
                <BarChart3 size={17} />
                <span>Track price trends</span>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <div className="route-visual">
              <div className="route-topline">
                <span>LIVE ROUTE ANALYSIS</span>

                <span className="route-status">
                  <i /> Updated now
                </span>
              </div>

              <div className="route-map">
                <div className="map-grid" />

                <div className="map-line line-one" />
                <div className="map-line line-two" />
                <div className="map-line line-three" />

                <div className="airport airport-delhi">
                  <span className="airport-dot" />

                  <div>
                    <strong>
                      {cleanFrom
                        ? cleanFrom.slice(0, 3).toUpperCase()
                        : "DEL"}
                    </strong>

                    <small>{cleanFrom || "Delhi"}</small>
                  </div>
                </div>

                <div className="airport airport-mumbai">
                  <span className="airport-dot" />

                  <div>
                    <strong>
                      {cleanTo
                        ? cleanTo.slice(0, 3).toUpperCase()
                        : "BOM"}
                    </strong>

                    <small>{cleanTo || "Mumbai"}</small>
                  </div>
                </div>

                <div className="route-plane">
                  <Plane size={20} />
                </div>

                <div className="route-distance">
                  <span>Direct route</span>
                  <strong>
                    {routeData?.distance || "1,148 km"}
                  </strong>
                </div>
              </div>

              <div className="route-bottom">
                <div>
                  <span>Current index</span>
                  <strong>{routeData?.index ?? "72.4"}</strong>
                </div>

                <div>
                  <span>Average fare</span>
                  <strong>
                    {routeData
                      ? formatCurrency(routeData.averageFare)
                      : "₹7,840"}
                  </strong>
                </div>

                <div className="route-change">
                  <TrendingDown size={15} />
                  <span>
                    {routeData?.priceChange
                      ? `${routeData.priceChange} lower`
                      : "8.2% lower"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
      ) : (
        <section className="dashboard-section" id="dashboard">
          <div className="dashboard-heading">
            <div>
              <div className="breadcrumb">
                AeroIndex <span>/</span> Route analysis
              </div>

              <h2>
                {cleanFrom}
                <ArrowRight size={24} />
                {cleanTo}
              </h2>

              <p>Live airfare comparison across available airlines</p>
            </div>

            <button
              className="edit-route-btn"
              onClick={handleEditRoute}
            >
              <Search size={16} />
              Edit route
            </button>
          </div>

          <div className="stats-grid">
            <div className="stat-card index-card">
              <div className="stat-top">
                <span>Airfare Index</span>

                <div className="status-pill">
                  <span /> Below average
                </div>
              </div>

              <div className="index-score">
                {routeData?.index ?? "--"} <span>/ 100</span>
              </div>

              <div className="index-progress">
                <div style={{ width: `${progressWidth}%` }} />
              </div>

              <div className="stat-bottom">
                <span>Based on current market prices</span>
                <TrendingDown size={17} />
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">
                <CircleDollarSign size={17} />
                Average fare
              </div>

              <div className="stat-value">
                {routeData
                  ? formatCurrency(routeData.averageFare)
                  : "--"}
              </div>

              <div className="stat-change positive">
                <TrendingDown size={15} />
                {routeData?.priceChange || "--"} below last month
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">
                <Clock3 size={17} />
                Best time to book
              </div>

              <div className="stat-value">
                {routeData?.bestBookingWindow || "--"}
              </div>

              <div className="stat-change neutral">
                <CalendarDays size={15} />
                Before departure
              </div>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="panel chart-panel">
              <div className="panel-heading">
                <div>
                  <span className="panel-kicker">
                    PRICE MOVEMENT
                  </span>

                  <h3>How fares are moving</h3>
                </div>

                <div className="period-tabs">
                  {["Weekly", "Monthly", "Yearly"].map((item) => (
                    <button
                      key={item}
                      className={period === item ? "active" : ""}
                      onClick={() => setPeriod(item)}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>

              <div className="chart-legend">
                <span>
                  <i className="legend-dot average" />
                  Average fare
                </span>

                <span>
                  <i className="legend-dot lowest" />
                  Lowest fare
                </span>
              </div>

              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={chartData[period]}
                    margin={{
                      top: 20,
                      right: 10,
                      left: 0,
                      bottom: 0,
                    }}
                  >
                    <defs>
                      <linearGradient
                        id="avgGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="0%"
                          stopColor="#3155a5"
                          stopOpacity={0.18}
                        />

                        <stop
                          offset="100%"
                          stopColor="#3155a5"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      strokeDasharray="4 4"
                      stroke="#e5e9f0"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="name"
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fill: "#8c96a7",
                        fontSize: 12,
                      }}
                    />

                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fill: "#8c96a7",
                        fontSize: 12,
                      }}
                      tickFormatter={(value) =>
                        `₹${value / 1000}k`
                      }
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#172235",
                        border: "1px solid #30425b",
                        borderRadius: "12px",
                        color: "#fff",
                      }}
                      formatter={(value) => [
                        `₹${value.toLocaleString("en-IN")}`,
                        "",
                      ]}
                    />

                    <Area
                      type="monotone"
                      dataKey="avg"
                      stroke="#3155a5"
                      strokeWidth={3}
                      fill="url(#avgGradient)"
                    />

                    <Area
                      type="monotone"
                      dataKey="low"
                      stroke="#b9c2d0"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      fill="none"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="panel insight-panel">
              <div className="panel-kicker">SMART INSIGHT</div>

              <div className="insight-icon">
                <Sparkles size={22} />
              </div>

              <h3>Prices look favourable</h3>

              <p>
                Current fares are{" "}
                <strong>
                  {routeData?.priceChange || "8.2%"} lower
                </strong>{" "}
                than the previous month. This could be a good time
                to book.
              </p>

              <div className="insight-route">
                <div className="insight-route-line" />

                <span>{cleanFrom}</span>
                <ArrowRight size={15} />
                <span>{cleanTo}</span>
              </div>

              <button
                className="insight-btn"
                onClick={() =>
                  alert(
                    `Booking options for ${cleanFrom} → ${cleanTo} will appear here when the booking API is connected.`
                  )
                }
              >
                View booking options
                <ArrowUpRight size={16} />
              </button>
            </div>
          </div>

          <div className="panel airlines-panel">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">
                  AIRLINE COMPARISON
                </span>

                <h3>Find the best fare</h3>
              </div>

              <button
                className="view-all-btn"
                onClick={() =>
                  alert("All available airlines will appear here.")
                }
              >
                View all
                <ArrowRight size={15} />
              </button>
            </div>

            <div className="airline-list">
              {dashboardAirlines.length > 0 ? (
                dashboardAirlines.map((airline, index) => (
                  <div
                    className="airline-row"
                    key={airline.name}
                  >
                    <div className="airline-name">
                      <div className="airline-logo">
                        {airline.code}
                      </div>

                      <div>
                        <strong>{airline.name}</strong>

                        {index === 0 && (
                          <span className="best-badge">
                            BEST VALUE
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="airline-metric">
                      <span>Lowest fare</span>
                      <strong>{airline.price}</strong>
                    </div>

                    <div className="airline-metric">
                      <span>Average fare</span>
                      <strong>{airline.avg}</strong>
                    </div>

                    <div className="airline-metric difference">
                      <span>Difference</span>
                      <strong>{airline.diff}</strong>
                    </div>

                    <button
                      className="airline-arrow"
                      onClick={() =>
                        alert(
                          `${airline.name} booking options will appear here.`
                        )
                      }
                    >
                      <ArrowUpRight size={17} />
                    </button>
                  </div>
                ))
              ) : (
                <div
                  style={{
                    padding: "28px 0",
                    textAlign: "center",
                    color: "#8c96a7",
                  }}
                >
                  No airline data available for this route yet.
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      <footer className="footer">
        <div className="brand">
          <div className="brand-mark">
            <Plane size={17} />
          </div>

          <span>
            Aero<span>Index</span>
          </span>
        </div>

        <span>Airfare intelligence, simplified.</span>
      </footer>
    </main>
  );
}

export default App;
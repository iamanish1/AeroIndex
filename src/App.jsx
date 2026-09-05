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

const fallbackChartData = {
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

async function getAirfareData(from, to) {
  const refreshResponse = await fetch(
    "http://127.0.0.1:5000/api/refresh",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from,
        to,
      }),
    }
  );

  if (!refreshResponse.ok) {
    throw new Error("Pipeline start nahi ho paaya.");
  }

  // Pipeline ko start hone ka time do
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // Pipeline complete hone tak status check karo
  for (let attempt = 0; attempt < 120; attempt++) {
    const statusResponse = await fetch(
      "http://127.0.0.1:5000/api/refresh-status"
    );

    const statusData = await statusResponse.json();

    if (!statusData.running) {
      break;
    }

    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  const response = await fetch(
    `http://127.0.0.1:5000/api/airfare?from=${encodeURIComponent(
      from
    )}&to=${encodeURIComponent(to)}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Unable to fetch airfare data");
  }

  return data;
}

function formatCurrency(value) {
  const amount = Number(value);

  if (!Number.isFinite(amount)) {
    return "--";
  }

  return `₹${Math.round(amount).toLocaleString("en-IN")}`;
}

function formatAirlineData(airline, averageFare) {
  const fare = Number(
    airline.fare || airline.lowestFare || airline.averageFare || 0
  );

  const average = Number(averageFare || 0);

  const airlineCodes = {
    IndiGo: "6E",
    "Air India": "AI",
    "Air India Express": "IX",
    "Akasa Air": "QP",
    Vistara: "UK",
    SpiceJet: "SG",
  };

  const difference =
    average > 0 ? ((fare - average) / average) * 100 : null;

  return {
    name: airline.name || "Unknown Airline",

    code:
      airline.code ||
      airlineCodes[airline.name] ||
      String(airline.name || "NA")
        .slice(0, 2)
        .toUpperCase(),

    price: formatCurrency(fare),

    avg: formatCurrency(airline.averageFare || fare),

    diff:
      difference === null
        ? "--"
        : `${difference > 0 ? "+" : ""}${difference.toFixed(1)}%`,

    isCheaper: difference !== null && difference < 0,
  };
}

function createLiveChartData(history, averageFare, period) {
  if (Array.isArray(history) && history.length > 1) {
    return history.map((item) => ({
      name: item.name || item.date,
      avg: Number(item.avg || item.averageFare || 0),
      low: Number(item.low || item.lowestFare || 0),
    }));
  }

  const average = Number(averageFare || 0);

  if (!Number.isFinite(average) || average <= 0) {
    return fallbackChartData[period];
  }

  if (period === "Weekly") {
    return [
      {
        name: "Mon",
        avg: Math.round(average * 0.96),
        low: Math.round(average * 0.82),
      },
      {
        name: "Tue",
        avg: Math.round(average * 0.98),
        low: Math.round(average * 0.84),
      },
      {
        name: "Wed",
        avg: Math.round(average * 1.02),
        low: Math.round(average * 0.87),
      },
      {
        name: "Thu",
        avg: Math.round(average * 0.99),
        low: Math.round(average * 0.85),
      },
      {
        name: "Fri",
        avg: Math.round(average * 1.04),
        low: Math.round(average * 0.89),
      },
      {
        name: "Sat",
        avg: Math.round(average * 1.01),
        low: Math.round(average * 0.86),
      },
      {
        name: "Sun",
        avg: Math.round(average),
        low: Math.round(average * 0.84),
      },
    ];
  }

  if (period === "Monthly") {
    return [
      {
        name: "Week 1",
        avg: Math.round(average * 0.97),
        low: Math.round(average * 0.83),
      },
      {
        name: "Week 2",
        avg: Math.round(average * 0.99),
        low: Math.round(average * 0.85),
      },
      {
        name: "Week 3",
        avg: Math.round(average * 1.03),
        low: Math.round(average * 0.88),
      },
      {
        name: "Week 4",
        avg: Math.round(average),
        low: Math.round(average * 0.84),
      },
    ];
  }

  return [
    {
      name: "Jan",
      avg: Math.round(average * 0.94),
      low: Math.round(average * 0.81),
    },
    {
      name: "Mar",
      avg: Math.round(average * 0.98),
      low: Math.round(average * 0.84),
    },
    {
      name: "May",
      avg: Math.round(average * 1.02),
      low: Math.round(average * 0.87),
    },
    {
      name: "Jul",
      avg: Math.round(average * 1.06),
      low: Math.round(average * 0.9),
    },
    {
      name: "Sep",
      avg: Math.round(average * 1.01),
      low: Math.round(average * 0.86),
    },
    {
      name: "Nov",
      avg: Math.round(average),
      low: Math.round(average * 0.84),
    },
  ];
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
        err.message ||
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

  const averageFare = Number(routeData?.averageFare || 0);
  const indexValue = Number(routeData?.index || 0);

  const dashboardAirlines = (routeData?.airlines || [])
    .map((airline) => formatAirlineData(airline, averageFare))
    .sort((a, b) => {
      const priceA = Number(a.price.replace(/[₹,]/g, "") || 0);
      const priceB = Number(b.price.replace(/[₹,]/g, "") || 0);

      return priceA - priceB;
    });

  const progressWidth = Math.min(
    Math.max(((indexValue - 100) / 50) * 100, 0),
    100
  );

  const liveChartData = createLiveChartData(
    routeData?.history || [],
    averageFare,
    period
  );

  const bookingUrl =
    routeData?.bookingUrl || "https://www.google.com/travel/flights";

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
                {loading ? "Updating..." : "Get Index"}
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
                  <strong>{routeData?.index ?? "--"}</strong>
                </div>

                <div>
                  <span>Average fare</span>

                  <strong>
                    {routeData
                      ? formatCurrency(routeData.averageFare)
                      : "--"}
                  </strong>
                </div>

                <div className="route-change">
                  <TrendingDown size={15} />

                  <span>
                    {routeData?.priceChange || "Live data"}
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
                  <span />

                  {indexValue > 100
                    ? "Above cheapest fare"
                    : "At cheapest fare"}
                </div>
              </div>

              <div className="index-score">
                {routeData?.index ?? "--"}
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
                {routeData?.priceChange || "Live data"}
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
                  <span className="panel-kicker">PRICE MOVEMENT</span>
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
                    data={liveChartData}
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
                        `₹${Math.round(value / 1000)}k`
                      }
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#172235",
                        border: "1px solid #30425b",
                        borderRadius: "12px",
                        color: "#fff",
                      }}
                      formatter={(value, name) => [
                        formatCurrency(value),
                        name === "avg"
                          ? "Average fare"
                          : "Lowest fare",
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

              <h3>Live airfare analysis</h3>

              <p>
                Current average fare is{" "}
                <strong>
                  {routeData
                    ? formatCurrency(routeData.averageFare)
                    : "--"}
                </strong>
                . This index is calculated from the latest collected Google
                Flights fare records.
              </p>

              <div className="insight-route">
                <div className="insight-route-line" />

                <span>{cleanFrom}</span>
                <ArrowRight size={15} />
                <span>{cleanTo}</span>
              </div>

              <button
                className="insight-btn"
                onClick={() => window.open(bookingUrl, "_blank")}
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
                  alert("All available airlines are already shown below.")
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
                    key={`${airline.name}-${index}`}
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

                      <strong
                        style={{
                          color: airline.isCheaper
                            ? "#16a34a"
                            : "#3155a5",
                        }}
                      >
                        {airline.diff}
                      </strong>
                    </div>

                    <button
                      className="airline-arrow"
                      onClick={() => window.open(bookingUrl, "_blank")}
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

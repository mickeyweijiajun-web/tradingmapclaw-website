/*!
 * tmc-events.js — TradingMapClaw anonymous, privacy-friendly event tracking.
 *
 * Off by default. Reads site/data/site-config.json's `analytics_enabled` flag:
 *   - false (default): window.tmcEvent(name) only logs to console.debug. No
 *     network requests, no cookies, no fingerprinting, no third-party script.
 *   - true: events are sent to GoatCounter (a privacy-friendly, cookie-less
 *     analytics endpoint) via a dynamically-injected script — never loaded
 *     unless explicitly enabled.
 *
 * Supported event names (see docs/SPEC_SITE_PHASE2.md §E):
 *   page_view, newsletter_click, newsletter_submit, radar_view, product_click,
 *   payhip_click, skill_click, consulting_mail_click, github_click
 *   (consulting_mail_click is the site's implementation of "consulting_click")
 *
 * Usage:
 *   window.tmcEvent('radar_view');
 *   <a data-tmc-event="github_click" href="...">...</a>  (auto-wired below)
 */
(function () {
  "use strict";

  // Reserved GoatCounter endpoint — only ever contacted when analytics_enabled
  // is true in site/data/site-config.json. No other third-party script is
  // loaded by this file under any configuration.
  var GOATCOUNTER_ENDPOINT = "https://tradingmapclaw.goatcounter.com/count";

  var config = { analytics_enabled: false, cta_variant: "A" };
  var goatcounterReady = false;

  function loadConfig(callback) {
    fetch("/data/site-config.json", { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("config fetch failed");
        return res.json();
      })
      .then(function (json) {
        config.analytics_enabled = !!json.analytics_enabled;
        config.cta_variant = json.cta_variant || "A";
      })
      .catch(function () {
        // Fail closed: analytics stays disabled if config can't be read.
        config.analytics_enabled = false;
      })
      .finally(function () {
        if (callback) callback();
      });
  }

  function injectGoatCounter() {
    if (goatcounterReady || !config.analytics_enabled) return;
    var script = document.createElement("script");
    script.async = true;
    script.setAttribute("data-goatcounter", GOATCOUNTER_ENDPOINT);
    script.src = "https://gc.zgo.at/count.js";
    document.head.appendChild(script);
    goatcounterReady = true;
  }

  function sendEvent(name, detail) {
    if (!config.analytics_enabled) {
      // Privacy-first default: no network call, just a debug breadcrumb.
      if (window.console && window.console.debug) {
        console.debug("[tmc-events] (disabled) " + name, detail || {});
      }
      return;
    }
    injectGoatCounter();
    // GoatCounter's own script exposes window.goatcounter.count once loaded;
    // until then, queue a best-effort direct pixel call as a fallback.
    var path = "/tmc-event/" + encodeURIComponent(name);
    var title = name;
    try {
      if (window.goatcounter && typeof window.goatcounter.count === "function") {
        window.goatcounter.count({ path: path, title: title, event: true });
      } else {
        var img = new Image();
        img.referrerPolicy = "origin";
        img.src =
          GOATCOUNTER_ENDPOINT +
          "?p=" + encodeURIComponent(path) +
          "&t=" + encodeURIComponent(title) +
          "&e=true";
      }
    } catch (e) {
      /* fail silent: analytics must never break the page */
    }
  }

  // Public API.
  window.tmcEvent = function (name, detail) {
    sendEvent(name, detail);
  };

  function wireDataAttributes() {
    var nodes = document.querySelectorAll("[data-tmc-event]");
    nodes.forEach(function (el) {
      var eventName = el.getAttribute("data-tmc-event");
      if (!eventName) return;
      var trigger = el.tagName === "FORM" ? "submit" : "click";
      el.addEventListener(trigger, function () {
        window.tmcEvent(eventName, { href: el.getAttribute("href") || null });
      });
    });
  }

  function init() {
    loadConfig(function () {
      window.tmcEvent("page_view", { path: window.location.pathname });
      wireDataAttributes();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

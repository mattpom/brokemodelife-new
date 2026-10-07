/* Distinct conversion-path event, separate from purchases and signups. */
(function () {
  document.addEventListener('click', function (event) {
    var element = event.target instanceof Element ? event.target : null;
    var link = element && element.closest('a[data-revenue-link],a[href]');
    if (!link || typeof window.gtag !== 'function') return;
    var url;
    try { url = new URL(link.href, window.location.href); } catch (_) { return; }
    var kind = link.dataset.revenueLink;
    var network = '';
    if (/(^|\.)amazon\.com$/.test(url.hostname)) {kind=url.searchParams.has('tag')?'affiliate':'retailer_reference';network='Amazon';}
    else if (/(^|\.)booking\.com$/.test(url.hostname)) {kind=url.searchParams.has('aid')?'affiliate':'retailer_reference';network='Booking.com';}
    else if (/(^|\.)getyourguide\.com$/.test(url.hostname)) {kind=url.searchParams.has('partner_id')?'affiliate':'retailer_reference';network='GetYourGuide';}
    else if (/(^|\.)etsy\.com$/.test(url.hostname)) kind='own_product';
    if (!kind) return;
    var asin=url.pathname.match(/\/(?:dp|gp\/product)\/([A-Z0-9]{10})/i);
    var listing=url.pathname.match(/\/listing\/(\d+)/);
    window.gtag('event','revenue_path_click',{
      destination_type:kind,
      affiliate_network:network,
      product_id:asin?asin[1]:(listing?listing[1]:''),
      source_page:window.location.pathname,
      destination_path:url.origin+url.pathname,
      link_position:link.dataset.position||link.dataset.product||'existing-link',
      transport_type:'beacon'
    });
  });
})();

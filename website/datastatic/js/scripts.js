
$(function () {

    // init feather icons
    feather.replace();

    // init tooltip & popovers
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();

    //page scroll
    $('a.page-scroll').bind('click', function (event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top - 20
        }, 1000);
        event.preventDefault();
    });

    // slick slider
    $('.slick-about').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 3000,
        dots: true,
        arrows: false
    });

    //toggle scroll menu
    var scrollTop = 0;
    $(window).scroll(function () {
        var scroll = $(window).scrollTop();
        //adjust menu background
        if (scroll > 80) {
            if (scroll > scrollTop) {
                $('.smart-scroll').addClass('scrolling').removeClass('up');
            } else {
                $('.smart-scroll').addClass('up');
            }
        } else {
            // remove if scroll = scrollTop
            $('.smart-scroll').removeClass('scrolling').removeClass('up');
        }

        scrollTop = scroll;

        // adjust scroll to top
        if (scroll >= 600) {
            $('.scroll-top').addClass('active');
        } else {
            $('.scroll-top').removeClass('active');
        }
        return false;
    });

    // scroll top top
    $('.scroll-top').click(function () {
        $('html, body').stop().animate({
            scrollTop: 0
        }, 1000);
    });

    /**Theme switcher - DEMO PURPOSE ONLY */
    $('.switcher-trigger').click(function () {
        $('.switcher-wrap').toggleClass('active');
    });
    $('.color-switcher ul li').click(function () {
        var color = $(this).attr('data-color');
        $('#theme-color').attr("href", "css/" + color + ".css");
        $('.color-switcher ul li').removeClass('active');
        $(this).addClass('active');
    });
});

function addfeature(mystr, targetMapId) {
    var ext = mystr.split(',')
        .map(function (val) { return parseFloat(val.trim()); })
        .filter(function (val) { return !isNaN(val); });

    if (ext.length !== 4) {
        console.error("Invalid extent: expected 4 numbers, got", ext.length, ext);
        return;
    }

    var minX = Math.min(ext[0], ext[2]);
    var maxX = Math.max(ext[0], ext[2]);
    var minY = Math.min(ext[1], ext[3]);
    var maxY = Math.max(ext[1], ext[3]);

    if (minX === maxX) {
        minX -= 0.0001;
        maxX += 0.0001;
    }
    if (minY === maxY) {
        minY -= 0.0001;
        maxY += 0.0001;
    }

    var validExt = [minX, minY, maxX, maxY];
    if (!validExt.every(Number.isFinite)) {
        console.error("Invalid extent values:", validExt);
        return;
    }

    var source = null;
    var mapInstance = null;

    // Try exact container id first (map-<id>)
    if (targetMapId) {
        if (window.metadataSources && window.metadataSources[targetMapId]) {
            source = window.metadataSources[targetMapId];
            mapInstance = window.metadataMaps ? window.metadataMaps[targetMapId] : null;
        }
        // try data-id mapping too
        if (!source && window.metadataSourcesByDataId && window.metadataSourcesByDataId[targetMapId]) {
            source = window.metadataSourcesByDataId[targetMapId];
            mapInstance = window.metadataMapsByDataId ? window.metadataMapsByDataId[targetMapId] : null;
        }
    }

    // If not found, prefer any visible metadata map
    if (!source && window.metadataSources && window.metadataMaps) {
        for (var key in window.metadataMaps) {
            if (!Object.prototype.hasOwnProperty.call(window.metadataMaps, key)) continue;
            var m = window.metadataMaps[key];
            var el = null;
            if (m && typeof m.getTargetElement === 'function') {
                el = m.getTargetElement();
            } else if (m && typeof m.getTarget === 'function') {
                var t = m.getTarget();
                el = typeof t === 'string' ? document.getElementById(t) : t;
            } else {
                el = document.getElementById(key);
            }
            if (el && el.offsetWidth > 0 && el.offsetHeight > 0) {
                source = window.metadataSources[key];
                mapInstance = m;
                break;
            }
        }
    }

    // Try visible maps by data-id mapping
    if (!source && window.metadataSourcesByDataId && window.metadataMapsByDataId) {
        for (var dataKey in window.metadataMapsByDataId) {
            if (!Object.prototype.hasOwnProperty.call(window.metadataMapsByDataId, dataKey)) continue;
            var m2 = window.metadataMapsByDataId[dataKey];
            var el2 = null;
            if (m2 && typeof m2.getTargetElement === 'function') {
                el2 = m2.getTargetElement();
            } else if (m2 && typeof m2.getTarget === 'function') {
                var t2 = m2.getTarget();
                el2 = typeof t2 === 'string' ? document.getElementById(t2) : t2;
            }
            if (el2 && el2.offsetWidth > 0 && el2.offsetHeight > 0) {
                source = window.metadataSourcesByDataId[dataKey];
                mapInstance = m2;
                break;
            }
        }
    }

    // Fallback: any metadata source
    if (!source && window.metadataSources) {
        var sourceKeys = Object.keys(window.metadataSources);
        if (sourceKeys.length) {
            source = window.metadataSources[sourceKeys[0]];
            mapInstance = window.metadataMaps ? window.metadataMaps[sourceKeys[0]] : null;
        }
    }

    // Last fallback to global vsource/map
    if (!source) {
        source = typeof vsource !== 'undefined' ? vsource : null;
    }
    if (!mapInstance) {
        mapInstance = typeof map !== 'undefined' ? map : null;
    }

    if (!source) {
        console.error("Unable to find a vector source for feature addition.");
        return;
    }
    if (!mapInstance) {
        console.error("Unable to find a map instance for view fitting.");
        return;
    }

    var feat = new ol.Feature(ol.geom.Polygon.fromExtent(validExt));
    source.addFeature(feat);

    function performFit() {
        if (!mapInstance) {
            return;
        }
        mapInstance.updateSize();
        mapInstance.getView().fit(validExt, {
            padding: [50, 50, 50, 50],
            size: mapInstance.getSize()
        });
        mapInstance.updateSize();
    }

    var mapTargetElement = null;
    if (targetMapId) {
        mapTargetElement = document.getElementById(targetMapId);
    } else if (mapInstance && typeof mapInstance.getTargetElement === 'function') {
        mapTargetElement = mapInstance.getTargetElement();
    }

    if (mapTargetElement && mapTargetElement.offsetWidth === 0 && mapTargetElement.offsetHeight === 0) {
        var collapseParent = mapTargetElement.closest('.collapse');
        if (collapseParent) {
            var onShown = function () {
                performFit();
                collapseParent.removeEventListener('shown.bs.collapse', onShown);
            };
            collapseParent.addEventListener('shown.bs.collapse', onShown);
        } else {
            window.setTimeout(performFit, 100);
        }
    } else {
        performFit();
    }
}
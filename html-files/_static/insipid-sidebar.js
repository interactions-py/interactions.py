$(document).ready(function () {
    'use strict';
    var $root = $(':root');
    var $body = $(document.body);
    var $overlay = $('#overlay');
    var $sidebar = $('.sphinxsidebar').first();
    var $sidebar_tabbable = $sidebar.find(':input, a[href], area[href], iframe');
    var $sidebar_button = $('#sidebar-button');

    $body.removeClass('sidebar-resizing');

    $sidebar.attr('id', 'sphinxsidebar');  // for aria-controls

    function updateSidebarAttributesVisible() {
        $sidebar_button.attr('title', "Collapse sidebar");
        $sidebar_button.attr('aria-label', "Collapse sidebar");
        $sidebar_button.attr('aria-expanded', true);
        $sidebar.attr('aria-hidden', false);
        $sidebar_tabbable.attr('tabindex', 0);
    }

    function updateSidebarAttributesHidden() {
        $sidebar_button.attr('title', "Expand sidebar");
        $sidebar_button.attr('aria-label', "Expand sidebar");
        $sidebar_button.attr('aria-expanded', false);
        $sidebar.attr('aria-hidden', true);
        $sidebar_tabbable.attr('tabindex', -1);
    }

    $sidebar.attr('tabindex', -1);
    if ($body.hasClass('sidebar-visible')) {
        updateSidebarAttributesVisible();
    } else {
        updateSidebarAttributesHidden();
    }

    function store(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
        }
    }

    function showSidebar() {
        $body.addClass('sidebar-visible');
        updateSidebarAttributesVisible();
        store('sphinx-sidebar', 'visible');
        $body.removeClass('topbar-folded');
        $sidebar[0].focus({preventScroll: true});
        $sidebar.blur();
    }

    function hideSidebar() {
        $body.removeClass('sidebar-visible');
        updateSidebarAttributesHidden();
        store('sphinx-sidebar', 'hidden');
        if (document.scrollingElement.scrollTop < $('#topbar').height()) {
            $body.removeClass('topbar-folded');
        } else {
            $body.addClass('topbar-folded');
        }
        document.scrollingElement.focus({preventScroll: true});
        document.scrollingElement.blur();
    }

    $sidebar_button.on('click', function () {
        if ($body.hasClass('sidebar-visible')) {
            $sidebar_button.blur();
            hideSidebar();
        } else {
            showSidebar();
        }
    });

    $sidebar_button.on('touchend', function ($event) {
        $('#topbar-placeholder').removeClass('fake-hover');
        $event.stopPropagation();
    });

    $overlay.on('click', function () {
        if ($body.hasClass('sidebar-visible')) {
            hideSidebar();
        }
    });

    var touchstart;

    document.addEventListener('touchstart', function (e) {
        if (e.touches.length > 1) { return; }
        var touch = e.touches[0];
        if (touch.clientX <= $sidebar.width()) {
            touchstart = {
                x: touch.clientX,
                y: touch.clientY,
                t: Date.now(),
            };
        }
    });

    document.addEventListener('touchend', function (e) {
        if (!touchstart) { return; }
        if (e.touches.length > 0 || e.changedTouches.length > 1) {
            touchstart = null;
            return;
        }
        var touch = e.changedTouches[0];
        var x = touch.clientX;
        var y = touch.clientY;
        var x_diff = x - touchstart.x;
        var y_diff = y - touchstart.y;
        var t_diff = Date.now() - touchstart.t;
        if (t_diff < 400 && Math.abs(x_diff) > Math.max(100, Math.abs(y_diff))) {
            if (x_diff > 0) {
                if (!$body.hasClass('sidebar-visible')) {
                    showSidebar();
                }
            } else {
                if ($body.hasClass('sidebar-visible')) {
                    hideSidebar();
                }
            }
        }
        touchstart = null;
    });

    $('.sidebar-resize-handle').on('mousedown', function (e) {
        $(window).on('mousemove', resize_mouse);
        $(window).on('mouseup', stop_resize_mouse);
        $body.addClass('sidebar-resizing');
        return false;  // Prevent unwanted text selection while resizing
    });

    $('.sidebar-resize-handle').on('touchstart', function (e) {
        e = e.originalEvent;
        if (e.touches.length > 1) { return; }
        $(window).on('touchmove', resize_touch);
        $(window).on('touchend', stop_resize_touch);
        $body.addClass('sidebar-resizing');
        return false;  // Prevent unwanted text selection while resizing
    });

    var ignore_resize = false;

    function resize_base(e) {
        if (ignore_resize) { return; }
        var window_width = $(window).width();
        var width = e.clientX;
        if (width > window_width) {
            $root.css('--sidebar-width', window_width + 'px');
        } else if (width > 10) {
            $root.css('--sidebar-width', width + 'px');
        } else {
            ignore_resize = true;
            hideSidebar();
        }
    }

    function resize_mouse(e) {
        resize_base(e.originalEvent);
    }

    function resize_touch(e) {
        e = e.originalEvent;
        if (e.touches.length > 1) { return; }
        resize_base(e.touches[0]);
    }

    function stop_resize_base() {
        if (ignore_resize) {
            $root.css('--sidebar-width', '19rem');
            ignore_resize = false;
        }
        store('sphinx-sidebar-width', $root.css('--sidebar-width'));
        $body.removeClass('sidebar-resizing');
    }

    function stop_resize_mouse(e) {
        $(window).off('mousemove', resize_mouse);
        $(window).off('mouseup', stop_resize_mouse);
        stop_resize_base();
    }

    function stop_resize_touch(e) {
        e = e.originalEvent;
        if (e.touches.length > 0 || e.changedTouches.length > 1) {
            return;
        }
        $(window).off('touchmove', resize_touch);
        $(window).off('touchend', stop_resize_touch);
        stop_resize_base();
    }

    $(window).on('resize', function () {
        var window_width = $(window).width();
        if (window_width < $sidebar.width()) {
            $root.css('--sidebar-width', window_width + 'px');
        }
    });

    // This is part of the sidebar code because it only affects the sidebar
    if (window.ResizeObserver) {
        const resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                let height;
                if (entry.borderBoxSize && entry.borderBoxSize.length > 0) {
                    height = entry.borderBoxSize[0].blockSize;
                } else {
                    height = entry.contentRect.height;
                }
                $root.css('--topbar-height', height + 'px');
            }
        });
        resizeObserver.observe(document.getElementById('topbar'));
    }

    var $current = $('.sphinxsidebar *:has(> a[href^="#"])');
    $current.addClass('current-page');
    if ($current.length) {
        var top = $current.offset().top;
        var height = $current.height();
        var topbar_height = $('#topbar').height();
        if (top < topbar_height || top + height > $sidebar.height()) {
            $current[0].scrollIntoView(true);
        }
    }

    $current.on('click', '> a', function () {
        if ($overlay.css('position') === 'fixed') {
            hideSidebar();
        }
    })

    if ($current.length == 1 && $current[0].childElementCount == 1 && $overlay.css('position') === 'fixed') {
        hideSidebar();
    }
});

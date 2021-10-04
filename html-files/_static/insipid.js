$(document).ready(function () {
    'use strict';

    // make sure all scripts are re-executed when navigating to cached page
    window.onunload = function () {};

    var $body = $(document.body);
    var $topbar = $('#topbar');
    var $topbar_placeholder = $('#topbar-placeholder');

    const threshold = 10;

    // auto-hide topbar
    function scroll_callback(scroller) {
        var ignore_scroll = true;
        var initial;
        var scroll_timeout;
        return function () {
            window.clearTimeout(scroll_timeout);
            var current = scroller.scrollTop;
            if (current <= $topbar.height() || (scroller.scrollHeight - current - scroller.clientHeight) < (scroller.clientHeight / 3)) {
                $body.removeClass('topbar-folded');
                ignore_scroll = true;
                return;
            } else if (ignore_scroll) {
                // We ignore single jumps
                ignore_scroll = false;
                initial = current;
            } else if (current - initial > threshold) {
                $body.addClass('topbar-folded');
                ignore_scroll = true;
                return;
            } else if (current - initial < -threshold) {
                $body.removeClass('topbar-folded');
                ignore_scroll = true;
                return;
            }
            scroll_timeout = setTimeout(function() {
                ignore_scroll = true;
            }, 66);
        };
    }

    $(document).on('scroll', scroll_callback(document.scrollingElement));

    var sidebar_scroller = document.querySelector('.sphinxsidebar');
    if (sidebar_scroller) {
        $(sidebar_scroller).on('scroll', scroll_callback(sidebar_scroller));
    }

    var div_body = document.querySelector('div.body');
    var first_section = document.querySelector('div.body .section, div.body section');
    if (first_section) {
        $(document).on('scroll', function () {
            if (window.pageYOffset >= div_body.offsetTop + first_section.offsetTop) {
                $body.addClass('scrolled');
            } else {
                $body.removeClass('scrolled');
            }
        });
        $(document).scroll();
    }

    $topbar.on('click', '.top', function () {
        $(document.scrollingElement).animate({scrollTop: 0}, 400).focus();
    });

    // show search
    var $search_form = $('#search-form');
    var $search_button = $('#search-button');
    $search_button.on('click', function () {
        try {
            // https://readthedocs-sphinx-search.readthedocs.io/
            showSearchModal();
            return;
        } catch(e) {}
        if ($search_form.is(':hidden')) {
            $search_form.show();
            $search_button.attr('aria-expanded', 'true');
            $search_form.find('input').focus();
            $body.removeClass('topbar-folded');
        } else {
            $search_form.hide();
            $search_button.attr('aria-expanded', 'false');
        }
    });

    if (document.fullscreenEnabled) {
        var $fullscreen_button = $('#fullscreen-button');
        $fullscreen_button.on('click', function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
            $fullscreen_button.blur();
            $topbar_placeholder.removeClass('fake-hover');
        });
    } else {
        $('#fullscreen-button').remove();
    }

    $topbar_placeholder.on('mouseenter', function() {
        $topbar_placeholder.addClass('fake-hover');
    });

    $topbar_placeholder.on('mouseleave', function() {
        $topbar_placeholder.removeClass('fake-hover');
    });

    $topbar_placeholder.on('touchend', function($event){
        if ($event.originalEvent.changedTouches[0].clientY < $topbar.height()) {
            $topbar_placeholder.addClass('fake-hover');
        }
        $event.stopPropagation();
    });

    $(window).on('touchmove touchend', function(){
        $topbar_placeholder.removeClass('fake-hover');
    });
});

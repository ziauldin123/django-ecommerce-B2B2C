(function($) {
    "use strict";

    let passiveSupported = false;

    try {
        const options = Object.defineProperty({}, 'passive', {
            get: function() {
                passiveSupported = true;
            }
        });

        window.addEventListener('test', null, options);
    } catch(err) {}

    let DIRECTION = null;

    function direction() {
        if (DIRECTION === null) {
            DIRECTION = getComputedStyle(document.body).direction;
        }

        return DIRECTION;
    }

    function isRTL() {
        return direction() === 'rtl';
    }

    $(function () {
        /*
        // Touch Click
        */
        function touchClick(elements, callback) {
            elements = $(elements);

            let touchStartData = null;

            const onTouchstart = function(event){
                const originalEvent = event.originalEvent;

                if (originalEvent.touches.length !== 1) {
                    touchStartData = null;
                    return;
                }

                touchStartData = {
                    target: originalEvent.currentTarget,
                    touch: originalEvent.changedTouches[0],
                    timestamp: (new Date).getTime(),
                };
            };
            const onTouchEnd = function(event){
                const originalEvent = event.originalEvent;

                if (
                    !touchStartData ||
                    originalEvent.changedTouches.length !== 1 ||
                    originalEvent.changedTouches[0].identity !== touchStartData.touch.identity
                ) {
                    return;
                }

                const timestamp = (new Date).getTime();
                const touch = originalEvent.changedTouches[0];
                const distance = Math.abs(
                    Math.sqrt(
                        Math.pow(touchStartData.touch.screenX - touch.screenX, 2) +
                        Math.pow(touchStartData.touch.screenY - touch.screenY, 2)
                    )
                );

                if (touchStartData.target === originalEvent.currentTarget && timestamp - touchStartData.timestamp < 500 && distance < 10) {
                    callback(event);
                }
            };

            elements.on('touchstart', onTouchstart);
            elements.on('touchend', onTouchEnd);

            return function() {
                elements.off('touchstart', onTouchstart);
                elements.off('touchend', onTouchEnd);
            };
        }

        // call this in touchstart/touchend event handler
        function preventTouchClick() {
            const onClick = function(event){
                event.preventDefault();

                document.removeEventListener('click', onClick);
            };
            document.addEventListener('click', onClick);
            setTimeout(function() {
                document.removeEventListener('click', onClick);
            }, 100);
        }


        /*
        // topbar dropdown
        */
        $('.topbar-dropdown__btn').on('click', function() {
            $(this).closest('.topbar-dropdown').toggleClass('topbar-dropdown--opened');
        });

        document.addEventListener('click', function(event) {
            $('.topbar-dropdown')
                .not($(event.target).closest('.topbar-dropdown'))
                .removeClass('topbar-dropdown--opened');
        }, true);

        touchClick(document, function(event) {
            $('.topbar-dropdown')
                .not($(event.target).closest('.topbar-dropdown'))
                .removeClass('topbar-dropdown--opened');
        });


        /*
        // search suggestions
        */
        $('.search').each(function(index, element) {
            let xhr;
            const search = $(element);
            const categories = search.find('.search__categories');
            const input = search.find('.search__input');
            const suggestions = search.find('.search__suggestions');
            const outsideClick = function(event) {
                // If the inner element still has focus, ignore the click.
                if ($(document.activeElement).closest('.search').is(search)) {
                    return;
                }

                if (!search.is($(event.target).closest('.search'))) {
                    close();
                }
            };
            const close = function() {
                search.removeClass('search--suggestions-open');
                updateLockState();
            };
            const open = function() {
                search.addClass('search--suggestions-open');
                updateLockState();
            };
            const updateLockState = function() {
                if (search.is('.search--has-suggestions.search--suggestions-open')) {
                    search.closest('.mobile-header').trigger('stroyka.header.lock');
                    search.closest('.nav-panel').trigger('stroyka.header.lock');
                } else {
                    search.closest('.mobile-header').trigger('stroyka.header.unlock');
                    search.closest('.nav-panel').trigger('stroyka.header.unlock');
                }
            };
            const setSuggestion = function(html) {
                const hasSuggestion = !!html;

                if (html) {
                    suggestions.html(html);
                }

                search.toggleClass('search--has-suggestions', hasSuggestion);

                updateLockState();
            };

            search.on('stroyka.search.open stroyka.search.close', function() {
                updateLockState();
            });
            search.on('focusout', function() {
                setTimeout(function(){
                    if (document.activeElement === document.body) {
                        return;
                    }

                    // Close suggestions if the focus received an external element.
                    if (!search.is($(document.activeElement).closest('.search'))) {
                        close();
                    }
                }, 10);
            });
            input.on('input', function() {
                if (xhr) {
                    // Abort previous AJAX request.
                    xhr.abort();
                }

                if (input.val()) {
                    // YOUR AJAX REQUEST HERE.
                    xhr = $.ajax({
                        url: 'suggestions.html',
                        success: function(data) {
                            xhr = null;
                            setSuggestion(data);
                        }
                    });
                } else {
                    // Remove suggestions.
                    setSuggestion('');
                }
            });
            input.on('focus', function() {
                open();
            });
            categories.on('focus', function() {
                close();
            });

            document.addEventListener('click', outsideClick, true);
            touchClick(document, outsideClick);

            if (input.is(document.activeElement)) {
                input.trigger('focus').trigger('input');
            }
        });


        /*
        // mobile search
        */
        const mobileSearch = $('.mobile-header__search');

        if (mobileSearch.length) {
            const open = function() {
                mobileSearch.addClass('mobile-header__search--open');
                mobileSearch.find('input')[0].focus();
                mobileSearch.trigger('stroyka.search.open');
            };
            const close = function() {
                mobileSearch.removeClass('mobile-header__search--open');
                mobileSearch.closest('.mobile-header').trigger('stroyka.header.unlock');
            };

            $('.indicator--mobile-search .indicator__button').on('click', function() {
                if (mobileSearch.is('.mobile-header__search--open')) {
                    close();
                } else {
                    open();
                }
            });

            mobileSearch.find('.search__button--type--close').on('click', function() {
                close();
            });

            document.addEventListener('click', function(event) {
                if (!$(event.target).closest('.indicator--mobile-search, .mobile-header__search').length) {
                    close();
                }
            }, true);
        }


        /*
        // nav-links
        */
        function CNavLinks(element) {
            this.element = $(element);
            this.items = this.element.find('.nav-links__item');
            this.currentItem = null;

            this.element.data('navLinksInstance', this);

            this.onMouseenter = this.onMouseenter.bind(this);
            this.onMouseleave = this.onMouseleave.bind(this);
            this.onGlobalTouchClick = this.onGlobalTouchClick.bind(this);
            this.onTouchClick = this.onTouchClick.bind(this);

            // add event listeners
            this.items.on('mouseenter', this.onMouseenter);
            this.items.on('mouseleave', this.onMouseleave);
            touchClick(document, this.onGlobalTouchClick);
            touchClick(this.items, this.onTouchClick);
        }
        CNavLinks.prototype.onGlobalTouchClick = function(event) {
            // check that the click was outside the element
            if (this.element.not($(event.target).closest('.nav-links')).length) {
                this.unsetCurrentItem();
            }
        };
        CNavLinks.prototype.onTouchClick = function(event) {
            if (event.cancelable) {
                const targetItem = $(event.currentTarget);

                if (this.currentItem && this.currentItem.is(targetItem)) {
                    return;
                }

                if (this.hasSubmenu(targetItem)) {
                    event.preventDefault();

                    if (this.currentItem) {
                        this.currentItem.trigger('mouseleave');
                    }

                    targetItem.trigger('mouseenter');
                }
            }
        };
        CNavLinks.prototype.onMouseenter = function(event) {
            this.setCurrentItem($(event.currentTarget));
        };
        CNavLinks.prototype.onMouseleave = function() {
            this.unsetCurrentItem();
        };
        CNavLinks.prototype.setCurrentItem = function(item) {
            this.currentItem = item;
            this.currentItem.addClass('nav-links__item--hover');

            this.openSubmenu(this.currentItem);
        };
        CNavLinks.prototype.unsetCurrentItem = function() {
            if (this.currentItem) {
                this.closeSubmenu(this.currentItem);

                this.currentItem.removeClass('nav-links__item--hover');
                this.currentItem = null;
            }
        };
        CNavLinks.prototype.hasSubmenu = function(item) {
            return !!item.children('.nav-links__submenu').length;
        };
        CNavLinks.prototype.openSubmenu = function(item) {
            const submenu = item.children('.nav-links__submenu');

            if (!submenu.length) {
                return;
            }

            submenu.addClass('nav-links__submenu--display');

            // calculate max height
            const submenuTop = submenu.offset().top - $(window).scrollTop();
            const viewportHeight = window.innerHeight;
            const paddingBottom = 20;

            submenu.css('maxHeight', (viewportHeight - submenuTop - paddingBottom) + 'px');
            submenu.addClass('nav-links__submenu--open');

            // megamenu position
            if (submenu.hasClass('nav-links__submenu--type--megamenu')) {
                const container = submenu.offsetParent();
                const containerWidth = container.width();
                const megamenuWidth = submenu.width();

                if (isRTL()) {
                    const itemPosition = containerWidth - (item.position().left + item.width());
                    const megamenuPosition = Math.round(Math.min(itemPosition, containerWidth - megamenuWidth));

                    submenu.css('right', megamenuPosition + 'px');
                } else {
                    const itemPosition = item.position().left;
                    const megamenuPosition = Math.round(Math.min(itemPosition, containerWidth - megamenuWidth));

                    submenu.css('left', megamenuPosition + 'px');
                }
            }
        };
        CNavLinks.prototype.closeSubmenu = function(item) {
            const submenu = item.children('.nav-links__submenu');

            if (!submenu.length) {
                return;
            }

            submenu.removeClass('nav-links__submenu--display');
            submenu.removeClass('nav-links__submenu--open');
            submenu.css('maxHeight', '');

            if (submenu && submenu.is('.nav-links__submenu--type--menu')) {
                const submenuInstance = submenu.find('> .menu').data('menuInstance');

                if (submenuInstance) {
                    submenuInstance.unsetCurrentItem();
                }
            }
        };

        $('.nav-links').each(function() {
            new CNavLinks(this);
        });


        /*
        // menu
        */
        function CMenu(element) {
            this.element = $(element);
            this.container = this.element.find('> .menu__submenus-container');
            this.items = this.element.find('> .menu__list > .menu__item');
            this.currentItem = null;

            this.element.data('menuInstance', this);

            this.onMouseenter = this.onMouseenter.bind(this);
            this.onMouseleave = this.onMouseleave.bind(this);
            this.onTouchClick = this.onTouchClick.bind(this);

            // add event listeners
            this.items.on('mouseenter', this.onMouseenter);
            this.element.on('mouseleave', this.onMouseleave);
            touchClick(this.items, this.onTouchClick);
        }
        CMenu.prototype.onMouseenter = function(event) {
            const targetItem = $(event.currentTarget);

            if (this.currentItem && targetItem.is(this.currentItem)) {
                return;
            }

            this.unsetCurrentItem();
            this.setCurrentItem(targetItem);
        };
        CMenu.prototype.onMouseleave = function() {
            this.unsetCurrentItem();
        };
        CMenu.prototype.onTouchClick = function(event) {
            const targetItem = $(event.currentTarget);

            if (this.currentItem && this.currentItem.is(targetItem)) {
                return;
            }

            if (this.hasSubmenu(targetItem)) {
                preventTouchClick();

                this.unsetCurrentItem();
                this.setCurrentItem(targetItem);
            }
        };
        CMenu.prototype.setCurrentItem = function(item) {
            this.currentItem = item;
            this.currentItem.addClass('menu__item--hover');

            this.openSubmenu(this.currentItem);
        };
        CMenu.prototype.unsetCurrentItem = function() {
            if (this.currentItem) {
                this.closeSubmenu(this.currentItem);

                this.currentItem.removeClass('menu__item--hover');
                this.currentItem = null;
            }
        };
        CMenu.prototype.getSubmenu = function(item) {
            let submenu = item.find('> .menu__submenu');

            if (submenu.length) {
                this.container.append(submenu);
                item.data('submenu', submenu);
            }

            return item.data('submenu');
        };
        CMenu.prototype.hasSubmenu = function(item) {
            return !!this.getSubmenu(item);
        };
        CMenu.prototype.openSubmenu = function(item) {
            const submenu = this.getSubmenu(item);

            if (!submenu) {
                return;
            }

            submenu.addClass('menu__submenu--display');

            // calc submenu position
            const menuTop = this.element.offset().top - $(window).scrollTop();
            const itemTop = item.find('> .menu__item-submenu-offset').offset().top - $(window).scrollTop();
            const viewportHeight = window.innerHeight;
            const paddingY = 20;
            const maxHeight = viewportHeight - paddingY * 2;

            submenu.css('maxHeight', maxHeight + 'px');

            const submenuHeight = submenu.height();
            const position = Math.min(
                Math.max(
                    itemTop - menuTop,
                    0
                ),
                (viewportHeight - paddingY - submenuHeight) - menuTop
            );

            submenu.css('top', position + 'px');
            submenu.addClass('menu__submenu--open');

            if (isRTL()) {
                const submenuLeft = this.element.offset().left - submenu.width();

                if (submenuLeft < 0) {
                    submenu.addClass('menu__submenu--reverse');
                }
            } else {
                const submenuRight = this.element.offset().left + this.element.width() + submenu.width();

                if (submenuRight > $('body').innerWidth()) {
                    submenu.addClass('menu__submenu--reverse');
                }
            }
        };
        CMenu.prototype.closeSubmenu = function(item) {
            const submenu = this.getSubmenu(item);

            if (submenu) {
                submenu.removeClass('menu__submenu--display');
                submenu.removeClass('menu__submenu--open');
                submenu.removeClass('menu__submenu--reverse');

                const submenuInstance = submenu.find('> .menu').data('menuInstance');

                if (submenuInstance) {
                    submenuInstance.unsetCurrentItem();
                }
            }
        };
        $('.menu').each(function(){
            new CMenu($(this));
        });


        /*
        // indicator (dropcart, drop search)
        */
        function CIndicator(element) {
            this.element = $(element);
            this.dropdown = this.element.find('.indicator__dropdown');
            this.button = this.element.find('.indicator__button');
            this.trigger = null;

            this.element.data('indicatorInstance', this);

            if (this.element.hasClass('indicator--trigger--hover')) {
                this.trigger = 'hover';
            } else if (this.element.hasClass('indicator--trigger--click')) {
                this.trigger = 'click';
            }

            this.onMouseenter = this.onMouseenter.bind(this);
            this.onMouseleave = this.onMouseleave.bind(this);
            this.onTransitionend = this.onTransitionend.bind(this);
            this.onClick = this.onClick.bind(this);
            this.onGlobalClick = this.onGlobalClick.bind(this);

            // add event listeners
            this.element.on('mouseenter', this.onMouseenter);
            this.element.on('mouseleave', this.onMouseleave);
            this.dropdown.on('transitionend', this.onTransitionend);
            this.button.on('click', this.onClick);
            $(document).on('click', this.onGlobalClick);
            touchClick(document, this.onGlobalClick);

            this.element.find('.search__input').on('keydown', function(event) {
                const ESC_KEY_CODE = 27;

                if (event.which === ESC_KEY_CODE) {
                    const instance = $(this).closest('.indicator').data('indicatorInstance');

                    if (instance) {
                        instance.close();
                    }
                }
            });
        }
        CIndicator.prototype.toggle = function(){
            if (this.isOpen()) {
                this.close();
            } else {
                this.open();
            }
        };
        CIndicator.prototype.onMouseenter = function(){
            this.element.addClass('indicator--hover');

            if (this.trigger === 'hover') {
                this.open();
            }
        };
        CIndicator.prototype.onMouseleave = function(){
            this.element.removeClass('indicator--hover');

            if (this.trigger === 'hover') {
                this.close();
            }
        };
        CIndicator.prototype.onTransitionend = function(event){
            if (
                this.dropdown.is(event.target) &&
                event.originalEvent.propertyName === 'visibility' &&
                !this.isOpen()
            ) {
                this.element.removeClass('indicator--display');
            }
        };
        CIndicator.prototype.onClick = function(event){
            if (this.trigger !== 'click') {
                return;
            }

            if (event.cancelable) {
                event.preventDefault();
            }

            this.toggle();
        };
        CIndicator.prototype.onGlobalClick = function(event){
            // check that the click was outside the element
            if (this.element.not($(event.target).closest('.indicator')).length) {
                this.close();
            }
        };
        CIndicator.prototype.isOpen = function(){
            return this.element.is('.indicator--open');
        };
        CIndicator.prototype.open = function(){
            this.element.addClass('indicator--display');
            this.element.width(); // force reflow
            this.element.addClass('indicator--open');
            this.element.find('.search__input').focus();

            const dropdownTop = this.dropdown.offset().top - $(window).scrollTop();
            const viewportHeight = window.innerHeight;
            const paddingBottom = 20;

            this.dropdown.css('maxHeight', (viewportHeight - dropdownTop - paddingBottom) + 'px');
        };
        CIndicator.prototype.close = function(){
            this.element.removeClass('indicator--open');
        };
        CIndicator.prototype.closeImmediately = function(){
            this.element.removeClass('indicator--open');
            this.element.removeClass('indicator--display');
        };

        $('.indicator').each(function() {
            new CIndicator(this);
        });


        /*
        // departments, sticky header
        */
        $(function() {
            /*
            // departments
            */
            const CDepartments = function(element) {
                const self = this;

                element.data('departmentsInstance', self);

                this.element = element;
                this.container = this.element.find('.departments__submenus-container');
                this.linksWrapper = this.element.find('.departments__links-wrapper');
                this.body = this.element.find('.departments__body');
                this.button = this.element.find('.departments__button');
                this.items = this.element.find('.departments__item');
                this.mode = this.element.is('.departments--fixed') ? 'fixed' : 'normal';
                this.fixedBy = $(this.element.data('departments-fixed-by'));
                this.fixedHeight = 0;
                this.currentItem = null;

                if (this.mode === 'fixed' && this.fixedBy.length) {
                    this.fixedHeight = this.fixedBy.offset().top - this.body.offset().top + this.fixedBy.outerHeight();
                    this.body.css('height', this.fixedHeight + 'px');
                }

                this.linksWrapper.on('transitionend', function (event) {
                    if (event.originalEvent.propertyName === 'height') {
                        $(this).css('height', '');
                        $(this).closest('.departments').removeClass('departments--transition');
                    }
                });

                this.onButtonClick = this.onButtonClick.bind(this);
                this.onGlobalClick = this.onGlobalClick.bind(this);
                this.onMouseenter = this.onMouseenter.bind(this);
                this.onMouseleave = this.onMouseleave.bind(this);
                this.onTouchClick = this.onTouchClick.bind(this);

                // add event listeners
                this.button.on('click', this.onButtonClick);
                document.addEventListener('click', this.onGlobalClick, true);
                touchClick(document, this.onGlobalClick);
                this.items.on('mouseenter', this.onMouseenter);
                this.linksWrapper.on('mouseleave', this.onMouseleave);
                touchClick(this.items, this.onTouchClick);

            };
            CDepartments.prototype.onButtonClick = function(event) {
                event.preventDefault();

                if (this.element.is('.departments--open')) {
                    this.close();
                } else {
                    this.open();
                }
            };
            CDepartments.prototype.onGlobalClick = function(event) {
                if (this.element.not($(event.target).closest('.departments')).length) {
                    if (this.element.is('.departments--open')) {
                        this.close();
                    }
                }
            };
            CDepartments.prototype.setMode = function(mode) {
                this.mode = mode;

                if (this.mode === 'normal') {
                    this.element.removeClass('departments--fixed');
                    this.element.removeClass('departments--open');
                    this.body.css('height', 'auto');
                }
                if (this.mode === 'fixed') {
                    this.element.addClass('departments--fixed');
                    this.element.addClass('departments--open');
                    this.body.css('height', this.fixedHeight + 'px');
                    $('.departments__links-wrapper', this.element).css('maxHeight', '');
                }
            };
            CDepartments.prototype.close = function() {
                if (this.element.is('.departments--fixed')) {
                    return;
                }

                const content = this.element.find('.departments__links-wrapper');
                const startHeight = content.height();

                content.css('height', startHeight + 'px');
                this.element
                    .addClass('departments--transition')
                    .removeClass('departments--open');

                content.height(); // force reflow
                content.css('height', '');
                content.css('maxHeight', '');

                this.unsetCurrentItem();
            };
            CDepartments.prototype.closeImmediately = function() {
                if (this.element.is('.departments--fixed')) {
                    return;
                }

                const content = this.element.find('.departments__links-wrapper');

                this.element.removeClass('departments--open');

                content.css('height', '');
                content.css('maxHeight', '');

                this.unsetCurrentItem();
            };
            CDepartments.prototype.open = function() {
                const content = this.element.find('.departments__links-wrapper');
                const startHeight = content.height();

                this.element
                    .addClass('departments--transition')
                    .addClass('departments--open');

                const documentHeight = document.documentElement.clientHeight;
                const paddingBottom = 20;
                const contentRect = content[0].getBoundingClientRect();
                const endHeight = Math.min(content.height(), documentHeight - paddingBottom - contentRect.top);

                content.css('height', startHeight + 'px');
                content.height(); // force reflow
                content.css('maxHeight', endHeight + 'px');
                content.css('height', endHeight + 'px');
            };
            CDepartments.prototype.onMouseenter = function(event) {
                const targetItem = $(event.currentTarget);

                if (this.currentItem && targetItem.is(this.currentItem)) {
                    return;
                }

                this.unsetCurrentItem();
                this.setCurrentItem(targetItem);
            };
            CDepartments.prototype.onMouseleave = function() {
                this.unsetCurrentItem();
            };
            CDepartments.prototype.onTouchClick = function(event) {
                const targetItem = $(event.currentTarget);

                if (this.currentItem && this.currentItem.is(targetItem)) {
                    return;
                }

                if (this.hasSubmenu(targetItem)) {
                    preventTouchClick();

                    this.unsetCurrentItem();
                    this.setCurrentItem(targetItem);
                }
            };
            CDepartments.prototype.setCurrentItem = function(item) {
                this.unsetCurrentItem();

                this.currentItem = item;
                this.currentItem.addClass('departments__item--hover');

                this.openSubmenu(this.currentItem);
            };
            CDepartments.prototype.unsetCurrentItem = function() {
                if (this.currentItem) {
                    this.closeSubmenu(this.currentItem);

                    this.currentItem.removeClass('departments__item--hover');
                    this.currentItem = null;
                }
            };
            CDepartments.prototype.getSubmenu = function(item) {
                let submenu = item.find('> .departments__submenu');

                if (submenu.length) {
                    this.container.append(submenu);

                    item.data('submenu', submenu);
                }

                return item.data('submenu');
            };
            CDepartments.prototype.hasSubmenu = function(item) {
                return !!this.getSubmenu(item);
            };
            CDepartments.prototype.openSubmenu = function(item) {
                const submenu = this.getSubmenu(item);

                if (submenu) {
                    submenu.addClass('departments__submenu--open');

                    const documentHeight = document.documentElement.clientHeight;
                    const paddingBottom = 20;

                    if (submenu.hasClass('departments__submenu--type--megamenu')) {
                        const submenuTop = submenu.offset().top - $(window).scrollTop();
                        submenu.css('maxHeight', (documentHeight - submenuTop - paddingBottom) + 'px');
                    }

                    if (submenu.hasClass('departments__submenu--type--menu')) {
                        submenu.css('maxHeight', (documentHeight - paddingBottom - Math.min(
                            paddingBottom,
                            this.body.offset().top - $(window).scrollTop()
                        )) + 'px');

                        const submenuHeight = submenu.height();
                        const itemTop = this.currentItem.offset().top - $(window).scrollTop();
                        const containerTop = this.container.offset().top - $(window).scrollTop();

                        submenu.css('top', (Math.min(itemTop, documentHeight - paddingBottom - submenuHeight) - containerTop) + 'px');
                    }
                }
            };
            CDepartments.prototype.closeSubmenu = function(item) {
                const submenu = item.data('submenu');

                if (submenu) {
                    submenu.removeClass('departments__submenu--open');

                    if (submenu.is('.departments__submenu--type--menu')) {
                        submenu.find('> .menu').data('menuInstance').unsetCurrentItem();
                    }
                }
            };

            const departmentsElement = $('.departments');
            const departments = departmentsElement.length ? new CDepartments(departmentsElement) : null;


            /*
            // sticky nav-panel
            */
            const nav = $('.nav-panel--sticky');

            if (nav.length) {
                const mode = nav.data('sticky-mode') ? nav.data('sticky-mode') : 'alwaysOnTop'; // one of [alwaysOnTop, pullToShow]
                const media = matchMedia('(min-width: 992px)');
                const departmentsMode = departments ? departments.mode : null;

                let stuck = false;
                let shown = false;
                let locked = false;
                let lockedPosition = 0;
                let lockRequested = false;
                let scrollDistance = 0;
                let scrollPosition = 0;
                let positionWhenToFix = function() { return 0; };
                let positionWhenToStick = function() { return 0; };

                nav.on('stroyka.header.lock', function(){
                    lockRequested = true;
                });
                nav.on('stroyka.header.unlock', function(){
                    lockRequested = false;
                    unlock();
                });

                const closeAllSubmenus = function() {
                    if (departments) {
                        departments.closeImmediately();
                    }
                    $('.nav-links').data('navLinksInstance').unsetCurrentItem();
                    $('.indicator').each(function() {
                        $(this).data('indicatorInstance').closeImmediately();
                    });
                };
                const show = function() {
                    nav.addClass('nav-panel--show');
                    shown = true;
                    $(document).trigger('stroyka.header.sticky.show');
                };
                const hide = function() {
                    nav.removeClass('nav-panel--show');
                    shown = false;
                    $(document).trigger('stroyka.header.sticky.hide');
                };
                const lock = function() {
                    lockedPosition = Math.max(0, window.pageYOffset);
                    nav.css({
                        position: 'absolute',
                        top: lockedPosition,
                        width: '100%',
                    });
                    locked = true;
                };
                const unlock = function() {
                    nav.css({
                        position: '',
                        top: '',
                        width: '',
                    });
                    locked = false;
                };
                const onScroll = function() {
                    const scrollDelta = window.pageYOffset - scrollPosition;

                    if ((scrollDelta < 0) !== (scrollDistance < 0)) {
                        scrollDistance = 0;
                    }

                    scrollPosition = window.pageYOffset;
                    scrollDistance += scrollDelta;

                    if (lockRequested) {
                        if (scrollDistance > 0 && !locked) {
                            lock();
                        } else if (scrollDistance <= 0 && window.pageYOffset <= lockedPosition) {
                            unlock();
                        }

                        return;
                    }

                    if (window.pageYOffset > positionWhenToStick()) {
                        if (!stuck) {
                            nav.addClass('nav-panel--stuck');
                            nav.css('transitionDuration', '0s');

                            if (mode === 'alwaysOnTop') {
                                show();
                            }

                            nav.height(); // force reflow
                            nav.css('transitionDuration', '');
                            stuck = true;

                            if (departments && departmentsMode === 'fixed') {
                                departments.setMode('normal');
                            }

                            closeAllSubmenus();
                        }

                        if (mode === 'pullToShow') {
                            const distanceToShow = 10; // in pixels
                            const distanceToHide = 25; // in pixels

                            if (scrollDistance < -distanceToShow && !nav.hasClass('nav-panel--show')) {
                                show();
                            }
                            if (scrollDistance > distanceToHide && nav.hasClass('nav-panel--show')) {
                                hide();
                                closeAllSubmenus();
                            }
                        }
                    } else if (window.pageYOffset <= positionWhenToFix()) {
                        if (stuck) {
                            nav.removeClass('nav-panel--stuck');
                            stuck = false;
                            hide();

                            if (departments && departmentsMode === 'fixed') {
                                departments.setMode('fixed');
                            }

                            closeAllSubmenus();
                        }
                    }
                };

                const onMediaChange = function() {
                    if (media.matches) {
                        scrollDistance = 0;
                        scrollPosition = window.pageYOffset;

                        const navPanelTop = nav.offset().top;
                        const navPanelBottom = navPanelTop + nav.outerHeight();
                        const departmentsBottom = departments ? departments.body.offset().top + departments.body.outerHeight() : 0;

                        if (departments && departmentsMode === 'fixed' && departmentsBottom > navPanelBottom) {
                            positionWhenToFix = positionWhenToStick = function () {
                                return departmentsBottom;
                            };
                        } else {
                            if (mode === 'alwaysOnTop') {
                                positionWhenToFix = positionWhenToStick = function() {
                                    return navPanelTop;
                                };
                            } else {
                                positionWhenToFix = function () {
                                    return shown ? navPanelTop : navPanelBottom;
                                };
                                positionWhenToStick = function () {
                                    return navPanelBottom;
                                };
                            }
                        }

                        window.addEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);

                        onScroll();
                    } else {
                        if (stuck) {
                            nav.removeClass('nav-panel--stuck');
                            stuck = false;
                            hide();

                            if (departments && departmentsMode === 'fixed') {
                                departments.setMode('fixed');
                            }

                            closeAllSubmenus();
                        }

                        window.removeEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);
                    }
                };

                if (media.addEventListener) {
                    media.addEventListener('change', onMediaChange);
                } else {
                    media.addListener(onMediaChange);
                }

                onMediaChange();
            }


            /*
            // sticky mobile-header
            */
            const mobileHeader = $('.mobile-header--sticky');
            const mobileHeaderPanel = mobileHeader.find('.mobile-header__panel');

            if (mobileHeader.length) {
                const mode = mobileHeader.data('sticky-mode') ? mobileHeader.data('sticky-mode') : 'alwaysOnTop'; // one of [alwaysOnTop, pullToShow]
                const media = matchMedia('(min-width: 992px)');

                let stuck = false;
                let shown = false;
                let locked = false;
                let lockedPosition = 0;
                let lockRequested = false;
                let scrollDistance = 0;
                let scrollPosition = 0;
                let positionWhenToFix = 0;
                let positionWhenToStick = 0;

                mobileHeader.on('stroyka.header.lock', function(){
                    lockRequested = true;
                });
                mobileHeader.on('stroyka.header.unlock', function(){
                    lockRequested = false;
                    unlock();
                });

                const show = function() {
                    mobileHeader.addClass('mobile-header--show');
                    shown = true;
                    $(document).trigger('stroyka.header.sticky.show');
                };
                const hide = function() {
                    mobileHeader.removeClass('mobile-header--show');
                    shown = false;
                    $(document).trigger('stroyka.header.sticky.hide');
                };
                const lock = function() {
                    lockedPosition = Math.max(0, window.pageYOffset);
                    mobileHeaderPanel.css({
                        position: 'absolute',
                        top: lockedPosition,
                        width: '100%',
                    });
                    locked = true;
                };
                const unlock = function() {
                    mobileHeaderPanel.css({
                        position: '',
                        top: '',
                        width: '',
                    });
                    locked = false;
                };
                const onScroll = function() {
                    const scrollDelta = window.pageYOffset - scrollPosition;

                    if ((scrollDelta < 0) !== (scrollDistance < 0)) {
                        scrollDistance = 0;
                    }

                    scrollPosition = window.pageYOffset;
                    scrollDistance += scrollDelta;

                    if (lockRequested) {
                        if (scrollDistance > 0 && !locked) {
                            lock();
                        } else if (scrollDistance <= 0 && window.pageYOffset <= lockedPosition) {
                            unlock();
                        }

                        return;
                    }

                    if (window.pageYOffset > positionWhenToStick) {
                        if (!stuck) {
                            mobileHeader.addClass('mobile-header--stuck');
                            mobileHeaderPanel.css('transitionDuration', '0s');

                            if (mode === 'alwaysOnTop') {
                                show();
                            }

                            mobileHeader.height(); // force reflow
                            mobileHeaderPanel.css('transitionDuration', '');
                            stuck = true;
                        }

                        if (mode === 'pullToShow') {
                            if (window.pageYOffset > positionWhenToFix) {
                                const distanceToShow = 10; // in pixels
                                const distanceToHide = 25; // in pixels

                                if (scrollDistance < -distanceToShow && !shown) {
                                    show();
                                }
                                if (scrollDistance > distanceToHide && shown) {
                                    hide();
                                }
                            } else if (shown) {
                                hide();
                            }
                        }
                    } else if (window.pageYOffset <= positionWhenToFix) {
                        if (stuck) {
                            mobileHeader.removeClass('mobile-header--stuck');
                            stuck = false;
                            hide();
                        }
                    }
                };

                const onMediaChange = function() {
                    if (!media.matches) {
                        scrollDistance = 0;
                        scrollPosition = window.pageYOffset;
                        positionWhenToFix = mobileHeader.offset().top;
                        positionWhenToStick = positionWhenToFix + (mode === 'alwaysOnTop' ? 0 : mobileHeader.outerHeight());

                        window.addEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);

                        onScroll();
                    } else {
                        if (stuck) {
                            mobileHeader.removeClass('mobile-header--stuck');
                            mobileHeader.removeClass('mobile-header--show');
                            stuck = false;
                            shown = false;
                            $(document).trigger('stroyka.header.sticky.hide');
                        }

                        window.removeEventListener('scroll', onScroll, passiveSupported ? {passive: true} : false);
                    }
                };

                if (media.addEventListener) {
                    media.addEventListener('change', onMediaChange);
                } else {
                    media.addListener(onMediaChange);
                }

                onMediaChange();
            }
        });


        /*
        // offcanvas cart
        */
        (function() {
            const body = $('body');
            const cart = $('.dropcart--style--offcanvas');

            if (cart.length === 0) {
                return;
            }

            function cartIsHidden() {
                return window.getComputedStyle(cart[0]).visibility === 'hidden';
            }
            function showScrollbar() {
                body.css('overflow', '');
                body.css('paddingRight', '');
            }
            function hideScrollbar() {
                const bodyWidth = body.width();
                body.css('overflow', 'hidden');
                body.css('paddingRight', (body.width() - bodyWidth) + 'px');
            }
            function open() {
                hideScrollbar();

                cart.addClass('dropcart--open');
            }
            function close() {
                if (cartIsHidden()) {
                    showScrollbar();
                }

                cart.removeClass('dropcart--open');
            }

            $('[data-open="offcanvas-cart"]').on('click', function(event){
                if (!event.cancelable) {
                    return;
                }

                event.preventDefault();

                open();
            });

            cart.find('.dropcart__backdrop, .dropcart__close').on('click', function(){
                close();
            });

            cart.on('transitionend', function(event){
                if (cart.is(event.target) && event.originalEvent.propertyName === 'visibility' && cartIsHidden()) {
                    showScrollbar();
                }
            });
        })();
    });

})(jQuery);

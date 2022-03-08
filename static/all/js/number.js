(function ($) {
    "use strict";

    // CustomEvent polyfill
    try {
        new CustomEvent('IE has CustomEvent, but doesn\'t support constructor');
    } catch (e) {
        window.CustomEvent = function(event, params) {
            let evt;
            params = params || {
                bubbles: false,
                cancelable: false,
                detail: undefined
            };
            evt = document.createEvent('CustomEvent');
            evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
            return evt;
        };

        CustomEvent.prototype = Object.create(window.Event.prototype);
    }

    /**
     * @param {HTMLInputElement} input
     * @param {HTMLElement} sub
     * @param {HTMLElement} add
     */
    function CustomNumber(input, sub, add) {
        const self = this;

        this.input = input;
        this.sub = sub;
        this.add = add;

        this._subHandler = function () {
            self._change(-1);
            self._changeByTimer(-1);
        };
        this._addHandler = function () {
            self._change(1);
            self._changeByTimer(1);
        };

        this.sub.addEventListener('mousedown', this._subHandler, false);
        this.add.addEventListener('mousedown', this._addHandler, false);
    }

    CustomNumber.prototype = {
        destroy: function() {
            this.sub.removeEventListener('mousedown', this._subHandler, false);
            this.add.removeEventListener('mousedown', this._addHandler, false);
        },

        /**
         * @param {number} direction - one of [-1, 1]
         * @private
         */
        _change: function(direction) {
            const step = this._step();
            const min = this._min();
            const max = this._max();

            let value = this._value() + step * direction;

            if (max != null) {
                value = Math.min(max, value);
            }
            if (min != null) {
                value = Math.max(min, value);
            }

            const triggerChange = this.input.value !== value.toString();

            this.input.value = value;

            if (triggerChange) {
                this.input.dispatchEvent(new CustomEvent('change', {bubbles: true}));
            }
        },

        /**
         * @param {number} direction - one of [-1, 1]
         * @private
         */
        _changeByTimer: function(direction) {
            const self = this;

            let interval;
            const timer = setTimeout(function () {
                interval = setInterval(function () {
                    self._change(direction);
                }, 50);
            }, 300);

            const documentMouseUp = function () {
                clearTimeout(timer);
                clearInterval(interval);

                document.removeEventListener('mouseup', documentMouseUp, false);
            };

            document.addEventListener('mouseup', documentMouseUp, false);
        },

        /**
         * @return {number}
         * @private
         */
        _step: function() {
            let step = 1;

            if (this.input.hasAttribute('step')) {
                step = parseFloat(this.input.getAttribute('step'));
                step = isNaN(step) ? 1 : step;
            }

            return step;
        },

        /**
         * @return {?number}
         * @private
         */
        _min: function() {
            let min = null;
            if (this.input.hasAttribute('min')) {
                min = parseFloat(this.input.getAttribute('min'));
                min = isNaN(min) ? null : min;
            }

            return min;
        },

        /**
         * @return {?number}
         * @private
         */
        _max: function() {
            let max = null;
            if (this.input.hasAttribute('max')) {
                max = parseFloat(this.input.getAttribute('max'));
                max = isNaN(max) ? null : max;
            }

            return max;
        },

        /**
         * @return {number}
         * @private
         */
        _value: function() {
            let value = parseFloat(this.input.value);

            return isNaN(value) ? 0 : value;
        }
    };

    /** @this {HTMLElement} */
    $.fn.customNumber = function (options) {
        options = $.extend({destroy: false}, options);

        return this.each(function () {
            if (!$(this).is('.input-number')) {
                return;
            }

            /** @type {(undefined|CustomNumber)} */
            let instance = $(this).data('customNumber');

            if (instance && options.destroy) {  // destroy
                instance.destroy();
                $(this).removeData('customNumber');

            } else if (!instance && !options.destroy) {  // init
                instance = new CustomNumber(
                    this.querySelector('.input-number__input'),
                    this.querySelector('.input-number__sub'),
                    this.querySelector('.input-number__add')
                );
                $(this).data('customNumber', instance);
            }
        });
    };
})(jQuery);

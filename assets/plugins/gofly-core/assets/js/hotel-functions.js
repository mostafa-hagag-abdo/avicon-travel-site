jQuery(document).ready(function ($) {
    // Initialize hotel packages from localized data
    let packagesWithQty = gofly_core_hotel_ajax.packages.map(pkg => {
        const regularPrice = parseFloat(pkg.price) || 0;
        const hasSale = pkg.price_sale_on && pkg.price_sale;
        const salePrice = hasSale ? parseFloat(pkg.price_sale) : null;

        // Use sale price if available, otherwise regular price
        const effectivePrice = hasSale ? salePrice : regularPrice;

        return {
            type: pkg.hotel_pricing_package_typ || pkg.type,
            regular_price: regularPrice,
            sale_price: salePrice,
            has_sale: hasSale,
            price: effectivePrice, // This should be the effective price (sale if available)
            booking_date: '',
            quantity: 1,
            room_quantity: 1,
            rooms: [],
            calculated_price: effectivePrice,
            nights: 1
        };
    });

    // Handle booking date range (check-in & check-out)
    let bookingDates = {
        check_in: '',
        check_out: ''
    };

    /**
     * Calculate nights between check-in and check-out dates
     */
    function calculateNights() {
        if (!bookingDates.check_in || !bookingDates.check_out) {
            return 1; // default to 1 night
        }

        const checkIn = new Date(bookingDates.check_in);
        const checkOut = new Date(bookingDates.check_out);
        const timeDiff = checkOut.getTime() - checkIn.getTime();
        const nights = Math.ceil(timeDiff / (1000 * 3600 * 24));

        return nights > 0 ? nights : 1;
    }

    /**
     * Update room prices for all packages
     */
    function updateRoomPrices() {
        const totalRooms = $(".room-list .single-room").length;
        const nights = calculateNights();

        $(".hotel-room-list .accordion-item").each(function (index) {
            const $packageItem = $(this);
            const $priceElement = $packageItem.find(".room-price");

            if (packagesWithQty[index]) {
                const pkg = packagesWithQty[index];

                // Check if package has sale price
                if (pkg.has_sale && pkg.sale_price) {
                    const regularTotal = pkg.regular_price * totalRooms * nights;
                    const saleTotal = pkg.sale_price * totalRooms * nights;

                    // Update with sale price structure: <del>regular</del> sale
                    $priceElement.html('<del>' + gofly_core_hotel_ajax.currency_symbol + regularTotal.toFixed(2) + '</del> ' + gofly_core_hotel_ajax.currency_symbol + saleTotal.toFixed(2));

                    // Update package data with sale price (not regular price)
                    packagesWithQty[index].calculated_price = saleTotal;
                    packagesWithQty[index].effective_price = saleTotal;
                } else {
                    const regularTotal = pkg.regular_price * totalRooms * nights;

                    // Update with regular price only
                    $priceElement.html(gofly_core_hotel_ajax.currency_symbol + regularTotal.toFixed(2));

                    // Update package data with regular price
                    packagesWithQty[index].calculated_price = regularTotal;
                    packagesWithQty[index].effective_price = regularTotal;
                }

                packagesWithQty[index].nights = nights;
                packagesWithQty[index].room_quantity = totalRooms;
            }
        });
    }

    $(document).on('click', '#hotel-calendar-check', function (e) {
        e.preventDefault();

        // Get visible day/month values from the selected-date boxes
        const checkInText = $('.hotel-selected-date-checkin h6').text().trim(); // e.g. "12 November"
        const checkOutText = $('.hotel-selected-date-checkout h6').text().trim(); // e.g. "15 November"

        // Get the year from the checkout input using ID selector
        const checkoutInputVal = $('#hotel-details-checkout').val(); // format: YYYY-MM-DD
        const checkoutYear = checkoutInputVal ? checkoutInputVal.split('-')[0] : new Date().getFullYear();

        // Helper: convert "12 November" + 2025 → "2025-11-12"
        function parseDate(dayMonthText, year) {
            const [dayStr, monthName] = dayMonthText.split(' ');
            const day = dayStr.padStart(2, '0');
            const month = new Date(`${monthName} 1, ${year}`).getMonth() + 1;
            const monthStr = String(month).padStart(2, '0');
            return `${year}-${monthStr}-${day}`;
        }

        // Build final booking dates
        bookingDates.check_in = parseDate(checkInText, checkoutYear);
        bookingDates.check_out = parseDate(checkOutText, checkoutYear);

        // Update room prices when dates change
        updateRoomPrices();
    });

    /**
     * Helper: Get current room info from DOM
     */
    function getAllRoomData() {
        let roomData = [];

        $(".room-list .single-room").each(function (i) {
            const adults = parseInt($(this).find('input[name="adult_quantity"]').val(), 10) || 0;
            const children = parseInt($(this).find('input[name="child_quantity"]').val(), 10) || 0;

            roomData.push({
                room_number: i + 1,
                adults: adults,
                children: children,
                total_guests: adults + children
            });
        });

        return roomData;
    }

    /**
     * Update main package data and recalculate prices
     */
    function updatePackageRoomQuantities() {
        const totalRooms = $(".room-list .single-room").length;
        const roomDetails = getAllRoomData();

        // Update all packages
        packagesWithQty.forEach(pkg => {
            pkg.room_quantity = totalRooms;
            pkg.rooms = roomDetails;

            // Calculate total guest quantity
            let totalGuests = 0;
            roomDetails.forEach(r => {
                totalGuests += r.total_guests;
            });
            pkg.quantity = totalGuests;
        });

        // Update room prices
        updateRoomPrices();
    }

    //Quantity Update Guest
    function updateGuestSummary() {
        $('input[name$="_quantity"]').each(function () {
            const name = $(this).attr('name');
            const type = name.replace('_quantity', '');
            const total = parseInt($(this).val(), 10) || 0;
            $('#qnt-' + type).text(total);
        });
    }

    /**
     * Handle guest quantity changes (+/-)
     */
    $(document).on("click", ".hotel-guest-quantity__plus, .hotel-guest-quantity__minus", function (e) {
        e.preventDefault();

        const $btn = $(this);
        const $input = $btn.siblings(".quantity__input");
        let val = parseInt($input.val(), 10) || 0;

        if ($btn.hasClass("hotel-guest-quantity__plus")) {
            val++;
        } else if ($btn.hasClass("hotel-guest-quantity__minus") && val > 0) {
            val--;
        }

        $input.val(val);
        updatePackageRoomQuantities();
        updateGuestSummary();

    });

    /**
     * Handle room deletion
     */
    $(document).on("click", ".room-delete-btn", function () {
        $(this).closest(".single-room").remove();
        updatePackageRoomQuantities();
    });

    /**
     * Handle room add
     */
    $(document).on("click", ".hotel-room-add", function () {

        $(".hotel-room-list").addClass("loading");

        updatePackageRoomQuantities();

        setTimeout(() => {
            $(".hotel-room-list").removeClass("loading");
        }, 500);

    });

    /**
     * Handle booking date change
     */
    $(document).on("change", ".hotel-booking-date-input", function () {
        const idx = $(this).attr("name").split("_").pop();
        packagesWithQty[idx].booking_date = $(this).val();
    });


    /**
     * Add to cart with base pricing only
     */
    $(document).one("click", ".add-to-cart-btn", function (e) {
        e.preventDefault();

        var checkoutUrl = gofly_core_hotel_ajax.checkout_url;
        const idx = $(this).data("package-index");
        const pkg = packagesWithQty[idx];

        // Send only base package info, let backend calculate final prices
        const pricing = {
            label: pkg.type,
            base_price: pkg.has_sale ? pkg.sale_price : pkg.regular_price, // Per night base price
            regular_price: pkg.regular_price,
            price: pkg.has_sale ? pkg.sale_price : pkg.regular_price,
            has_sale: pkg.has_sale,
            quantity: pkg.quantity, // total guests
            room_quantity: pkg.room_quantity,
            nights: pkg.nights || calculateNights(),
            rooms: pkg.rooms
        };

        $.ajax({
            url: gofly_core_hotel_ajax.ajax_url,
            type: "POST",
            data: {
                action: "egns_hotel_add_to_cart",
                post_id: gofly_core_hotel_ajax.post_id,
                data: {
                    pricing: [pricing],
                    booking_date: bookingDates
                },
            },
            success: function (response) {
                // Redirect to Checkout page on success
                window.location.href = checkoutUrl;

                // Disable the button after it's clicked once
                $(this).prop('disabled', true);
            },
            error: function () {
                alert("Failed to add hotel room to cart.");
            }
        });
    });
    // Initialize once
    updatePackageRoomQuantities();
});
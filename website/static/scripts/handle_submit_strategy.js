// actualizes actual strategy_id in variables
$(document).ready(function () {

    $('.' + toggle_div.toggle_class).on('change', function () {

        // show and hide the parameter-div of the chosen dropdown-selection
        handle_submit_strategy_var.strategy_name = this.value
        console.log(this.value)
    });

})

// When page is loaded...
$(document).ready(function () {

    // ... disable apply button and ...
    handle_submit_strategy_var.actual_document.getElementById(handle_submit_strategy_var.disable_apply_button).disabled = true;
    
    // ... if the stock is traded in a strategy, a (!) will be added
    if (handle_submit_strategy_var.stocks_breakout.includes(handle_submit_strategy_var.stock_id) || handle_submit_strategy_var.stocks_breakdown.includes(handle_submit_strategy_var.stock_id) || handle_submit_strategy_var.stocks_bollinger.includes(handle_submit_strategy_var.stock_id)) {
        handle_submit_strategy_var.actual_document.getElementById(handle_submit_strategy_var.disable_apply_button).value = "Apply Strategy (!)";
    }
})
function myfunctionhandler(display) {
    if (handle_submit_strategy_var.stocks_breakout.includes(handle_submit_strategy_var.stock_id) || handle_submit_strategy_var.stocks_breakdown.includes(handle_submit_strategy_var.stock_id) || handle_submit_strategy_var.stocks_bollinger.includes(handle_submit_strategy_var.stock_id) ){
        handle_submit_strategy_var.actual_document.getElementById(handle_submit_strategy_var.show_placed_div).style.display = display;
        var disabled = true
        if(display == 'none'){
            disabled = false
        }
        else if (display == 'block'){
            disabled = true
        }
        handle_submit_strategy_var.actual_document.getElementById(handle_submit_strategy_var.disable_apply_button).disabled = disabled;

        return false;
    }
    else {
        return true;
    }
}
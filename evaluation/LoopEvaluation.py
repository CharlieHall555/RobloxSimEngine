def eval_for(state , for_loop : AST.ForNode):

    iterator : AST.VarNode = for_loop.iterator
    start : typing.Any = eval_expression(state , for_loop.start)
    end : typing.Any = eval_expression(state , for_loop.end)
    step : typing.Any = eval_expression(state , for_loop.step)

    i = start

    while i <= end:
        state.append({iterator.value: i})
        eval_block(state , for_loop.block)
        i += step
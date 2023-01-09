# These Matcher have been discarded, may be used future
class RandintMatcher(BaseMatcher):
    def get_paddle_nodes(self, args, kwargs): 
        args = self.parse_args(args)
        new_kwargs = {}
        if len(args) == 2:
            new_kwargs['low'] = '0'
            new_kwargs['high'] = args[0]
            new_kwargs['shape'] = args[1]
        elif len(args) == 3:
            new_kwargs['low'] = args[0]
            new_kwargs['high'] = args[1]
            new_kwargs['shape'] = args[2]
        else:
            return None

        new_kwargs.update(self.parse_kwargs(kwargs))
        if 'layout' in new_kwargs:
            del kwargs['layout']
        if 'device' in new_kwargs:
            del kwargs['device']
        if 'generator' in new_kwargs:
            del kwargs['generator']
        

        requires_grad_v = False
        if 'requires_grad' in new_kwargs:
            requires_grad_v = eval(new_kwargs.pop('requires_grad'))
        
        if requires_grad_v and 'out' in new_kwargs:
            out_v = kwargs.pop('out')
            API_TEMPLACE = textwrap.dedent(
                '''
                {} = paddle.randint({})
                {}.stop_gradient = False
                {}
                '''
            )
            code = API_TEMPLACE.format(out_v, self.kwargs_to_str(new_kwargs), out_v, out_v)
        elif requires_grad_v and 'out' not in new_kwargs:
            API_TEMPLACE = textwrap.dedent(
                '''
                {} = paddle.randint({})
                {}.stop_gradient = False
                {}
                '''
            )
            out = get_unique_name('out')
            code = API_TEMPLACE.format(out, self.kwargs_to_str(new_kwargs), out, out)
        elif not requires_grad_v and 'out' in kwargs:
            out_v = kwargs.pop('out')
            API_TEMPLACE = textwrap.dedent(
                '''
                {} = paddle.randint({})
                {}
                '''
            )
            code = API_TEMPLACE.format(out_v, self.kwargs_to_str(new_kwargs), out_v)
        else:
            code = 'paddle.randint({})'.format(self.kwargs_to_str(new_kwargs))

        return ast.parse(code).body


class TensorToMatcher(BaseMatcher):
    def get_paddle_class_nodes(self, func, args, kwargs):
        self.parse_func(func)
        
        if len(args)==1 and isinstance(args[0], ast.Str):
            dtype = self.parse_args(args)[0]
            code = '{}.astype(dtype={})'.format(self.paddleTensor, dtype)
            return ast.parse(code).body
        
        kwargs = self.parse_kwargs(kwargs)
        if len(kwargs)==1 and 'dtype' in kwargs:
            code = '{}.astype({})'.format(self.paddleTensor, self.kwargs_to_str(kwargs))
            return ast.parse(code).body

        return None

class TensorRequiresGradMatcher(BaseMatcher):
    def generate_code(self, kwargs):
        if 'requires_grad' in kwargs:
            API_TEMPLACE = textwrap.dedent(
                '''
                {} = {}
                {}.stop_gradient = not {}
                {}
                '''
            )
            out = get_unique_name('out')
            code = API_TEMPLACE.format(out, self.paddleClass, out, kwargs.pop('requires_grad'), self.paddleClass)
        else:
            API_TEMPLACE = textwrap.dedent(
                '''
                {} = {}
                {}.stop_gradient = False
                {}
                '''
            )
            out = get_unique_name('out')
            code = API_TEMPLACE.format(out, self.paddleClass, out, out)

        return code


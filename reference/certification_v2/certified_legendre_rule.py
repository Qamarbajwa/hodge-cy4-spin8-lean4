"""Optional Arb certified Gauss-Legendre roots/weights; seeds are not proofs."""
from fractions import Fraction as F
from math import cos,pi

from flint import arb,fmpq,ctx
from research.certification_v2.archimedean.arb_adapter import encoded_bounds,dyadic
from research.certification_v2.exact_interval_ldl import Interval


def point(q):
    q=F(q)
    return arb(fmpq(q.numerator,q.denominator))


def integer_power(value,exponent):
    if type(exponent) is not int or exponent<0:
        raise ValueError("nonnegative integer exponent required")
    result=arb(1)
    while exponent:
        if exponent%2:
            result=result*value
        value=value*value
        exponent//=2
    return result


def sign(value):
    if not value.is_finite():
        return 0
    return 1 if value.lower()>0 else -1 if value.upper()<0 else 0


def legendre_box(degree,box):
    """Native verified POINT polynomial plus global real derivative bound."""
    box=Interval.parse(box)
    if type(degree) is not int or degree<0 or box.lo < -1 or box.hi > 1:
        raise ValueError("nonnegative degree and interval in[-1,1] required")
    midpoint=(box.lo+box.hi)/2
    radius=(box.hi-box.lo)/2
    error=F(degree*(degree+1),2)*radius
    base=point(midpoint).legendre_p(degree)
    return base+arb(0,fmpq(error.numerator,error.denominator))


def certify_rule(n,bits=192,bracket_bits=80,newton_steps=8):
    if type(n) is not int or n<1 or type(bits) is not int or bits<64 or type(bracket_bits) is not int or bracket_bits<8 or type(newton_steps) is not int or newton_steps<1:
        raise ValueError("positive degree/steps and valid precision required")
    failures=[]
    roots=[]
    with ctx.workprec(bits):
        radius=F(1,2**bracket_bits)
        for k in range(1,n+1):
            seed=F.from_float(cos(pi*(k-F(1,4))/(n+F(1,2))))
            x=point(seed)
            # These Newton iterations only generate candidate centers. No
            # convergence/uniqueness statement is inferred from their success.
            for _ in range(newton_steps):
                pn=x.legendre_p(n)
                previous=x.legendre_p(n-1)
                derivative=n*(previous-x*pn)/(1-x*x)
                if not derivative.is_finite() or derivative.contains(0):
                    break
                update=x-pn/derivative
                if not update.is_finite():
                    break
                x=point(dyadic(update.mid()))
            center=dyadic(x.mid())
            box=Interval(center-radius,center+radius)
            if box.lo<=-1 or box.hi>=1:
                failures.append({"seed_index":k,"reason":"BRACKET_OUTSIDE_MINUS1_PLUS1","box":box.encoded()})
                continue
            left=point(box.lo).legendre_p(n)
            right=point(box.hi).legendre_p(n)
            sl,sr=sign(left),sign(right)
            if sl*sr != -1:
                failures.append({"seed_index":k,"reason":"ENDPOINT_SIGN_CHANGE_NOT_PROVED",
                                 "box":box.encoded(),"left":encoded_bounds(left) if left.is_finite() else None,
                                 "right":encoded_bounds(right) if right.is_finite() else None})
                continue
            roots.append({"node":box,"endpoint_signs":[sl,sr],"seed_index":k})
        roots.sort(key=lambda item:item["node"].lo)
        disjoint=all(roots[k]["node"].hi<roots[k+1]["node"].lo for k in range(len(roots)-1))
        if failures or len(roots)!=n or not disjoint:
            return {"status":"INCONCLUSIVE_ROOT_CERTIFICATION","degree":n,"precision_bits":bits,
                    "certified_brackets":len(roots),"disjoint":disjoint,"failures":failures,
                    "NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
        result=[]
        for root in roots:
            box=root["node"]
            previous=legendre_box(n-1,box)
            if not previous.is_finite() or previous.contains(0):
                failures.append({"seed_index":root["seed_index"],"reason":"WEIGHT_PREVIOUS_POLYNOMIAL_NOT_SEPARATED_FROM_ZERO"})
                continue
            xmid=(box.lo+box.hi)/2
            xrad=(box.hi-box.lo)/2
            x=arb(fmpq(xmid.numerator,xmid.denominator),fmpq(xrad.numerator,xrad.denominator))
            numerator=2*(1-x*x)
            denominator=n*n*previous*previous
            weight=numerator/denominator
            if not weight.is_finite() or weight.lower()<=0:
                failures.append({"seed_index":root["seed_index"],"reason":"POSITIVE_FINITE_WEIGHT_NOT_PROVED"})
                continue
            result.append({"node":box.encoded(),"weight":encoded_bounds(weight),
                           "endpoint_signs":root["endpoint_signs"],
                           "P_n_minus1_box":encoded_bounds(previous)})
    if failures or len(result)!=n:
        return {"status":"INCONCLUSIVE_WEIGHT_CERTIFICATION","degree":n,"precision_bits":bits,
                "certified_weights":len(result),"failures":failures,
                "NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}
    return {"status":"CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES","degree":n,"precision_bits":bits,
            "bracket_radius_exact":str(radius),"newton_steps_candidate_only":newton_steps,
            "root_proof":"N_DISJOINT_RATIONAL_STRICT_SIGN_CHANGES_PLUS_POLYNOMIAL_DEGREE_COUNT",
            "weight_proof":"2(1-x²)/(n² P_(n-1)(x)²) at true root; denominator separated",
            "interval_legendre_method":"NATIVE_ARB_POINT_EVAL_PLUS_GLOBAL_DERIVATIVE_BOUND",
            "nodes_weights":result,"NO_RH_PROOF":True,"full_operator_status":"BLOCKED"}


def moments(rule,indices):
    if rule["status"]!="CERTIFIED_GAUSS_LEGENDRE_RULE_BOXES":
        raise ValueError("uncertified rule cannot be used")
    result=[]
    with ctx.workprec(rule["precision_bits"]):
        nodes=[]
        for item in rule["nodes_weights"]:
            xb,wb=Interval.parse(item["node"]),Interval.parse(item["weight"])
            def ball(value):
                mid=(value.lo+value.hi)/2
                rad=(value.hi-value.lo)/2
                return arb(fmpq(mid.numerator,mid.denominator),fmpq(rad.numerator,rad.denominator))
            nodes.append((ball(xb),ball(wb)))
        for degree in indices:
            if type(degree) is not int or degree<0 or degree>2*rule["degree"]-1:
                raise ValueError("moment outside exact polynomial quadrature degree")
            value=sum((w*integer_power(x,degree) for x,w in nodes),arb(0))
            exact=F(0) if degree%2 else F(2,degree+1)
            bounds=Interval.parse(encoded_bounds(value))
            result.append({"degree":degree,"box":bounds.encoded(),"exact":str(exact),
                           "contained":bounds.lo<=exact<=bounds.hi})
    return result

import json
import os 
import re
import time
import logging 
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from strands import Agent,tool
from strands.models import BedrockModel
from docs import CONTRACTS ,IP_FINDINGS,FINANCIAL_FINDINGS,REGULATORY_FINDINGS
load_dotenv()

logging.basicConfig(level =logging.WARNING)

def clean_response(text:str) -> str:
    """Strip <thinking>...</thinking> tags from Nova model outputs."""
    return re.sub(r"<thinking>.*?</thinking>\s*","",str(text),flags= re.DOTALL).strip()


AWS_REGION = os.environ.get("AWS_REGION","us-east-1")
NOVA_LITE_MODEL = os.environ.get("NOVA_LITE_MODEL","amazon.nova-lite-v1:0")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL","us.anthropic.claude-sonnet-4-5-20250929-v1:0")
NOVA_PRO_MODEL = os.environ.get("NOVA_PRO_MODEL","amazon.nova-pro-v1:0")




regulatory_cache ={}
financial_cache ={}
ip_cache ={}



def build_regulatory_agent() -> Agent:
    """
    Build the Regulatory Compliance Agent using Nova Lite.
    """
    model = BedrockModel(
        model_id = NOVA_LITE_MODEL,
        region_name = AWS_REGION,
        temperature =0.0,
    )
    system_prompt ="""
    You are a Regulatory Compliance agent.Your ONLY job:
    1.call the check_regulatory tool with the contract_id
    2.Report in exactly 3 lines:
        Risk Level: <HIGH | MEDIUM| LOW>
        Violations :<count or NONE>
        Recommendation:<one-sentence>
    """

    @tool
    def check_regulatory(contract_id:str)->str:
        """
        Check contract for GDPR, SOX, HIPAA regulatory compliance.

        Examines :data residency, certifications, data processing agreements,
        retention policies, and cross-border transfer safeguards.

        Args:
        contact_id: The contract ID(e.g., "CONTRACT-001")

        Returns:
        JSON with regulatory compliance findings 
        """
        contract = next((c for c in CONTRACTS if c['id'] == contract_id),None)
        if not contract:
            return json.dumps({'error':f"Contract {contract_id} not found"})

        findings = REGULATORY_FINDINGS.get(contract_id)
        result ={
            "contract_id": contract_id,
            "domain":"regulatory_compliance",
            "risk_level" :findings.get("risk_level","UNKNOWN"),
            "frameworks_checked": findings.get("frameworks_checked",[]),
            'violations':findings.get("violations",[]),
            "recommendation":findings.get("recommendation",""),
        }
        regulatory_cache[contract_id] = result
        return json.dumps(result, indent=2)

    return Agent(
        model = model,
        system_prompt = system_prompt,
        tools =[check_regulatory]
    )



def build_financial_agent() ->Agent:
    """
    Build the Financial Risk Agent using Claude 
    """
    model =BedrockModel(
        model_id = CLAUDE_MODEL,
        region_name = AWS_REGION,
        temperature =0.0

    )
    system_prompt= """
        You are a Financial risk agent. You role is to
        1. call the assess_financial_risk with contract_id
        2.Request output in exactly 3 lines:
            Risk Level :<HIGH|MEDIUM|LOW>
            Unfavorable terms :<HIGH|MEDIUM|LOW>
            Recommendation : <HIGH|MEDIUM"LOW>
        """
    @tool
    def assess_financial_risk(contract_id:str) ->str:
        """
        Assess financial risk in contract terms.
        Examines: payment terms,liability caps, indemnification,
        penalty structures, and auto-renewal traps.

        Args:
        contract_id: The contract ID (e.g.. "CONTRACT-001")

        Returns:
        JSON with financial risk assessment
        """
        contract = next((c for c in CONTRACTS if c['id'] ==contract_id ))

        if not contract:
            return json.dumps({"error":f"Contract {contract_id} not found"})
        findings = FINANCIAL_FINDINGS.get(contract_id,{})
        result ={
            "contract_id":contract_id,
            "domain": "financial_risk",
            "contract_value":contract["value"],
            "risk_level": findings.get("risk_level","UNKNOWN"),
            "findings":findings.get("findings",[]),
            "unfavorable_terms": findings.get("unfavorable_terms",[]),
            "recommendation":findings.get("recommendation",""),


        }
        financial_cache[contract_id] = result
        return json.dumps(result, indent =2 )

    return Agent(
        model = model,
        system_prompt = system_prompt,
        tools =[assess_financial_risk],
    )


def build_ip_agent()-> Agent:
    """
    Build the IP protection Agent using Nova Pro
    """
    model = BedrockModel(
        model_id = NOVA_PRO_MODEL,
        region_name =AWS_REGION, 
        temperature =0.1

    )
    system_prompt ="""
        You are a ip protection agent. You role is only .
        1.call review_ip_clauses with the contract id 
        2. Request output in exactly 3 lines:
            Risk level :<HIGH|MEDIUM|LOW>
            IP concerns :<HIGH|MEDIUM"LOW>
            Recommendation :<HIGH|MEDIUM|LOW>
        """
    @tool
    def review_ip_clauses(contract_id:str) ->str:
        """
        Review ip ownership ,licensing, and non-compete clauses.

        Examines: IP assignment, work-for-hire provisions,licensing grants,
        NDA reprocity, and non-compete scope.

        Args:
            contract_id : The contract ID(e.g.. "CONTRACT-001")

        Returns:
            JSON with IP protection assessment
        """
        contract = next((c for c in CONTRACTS if c['id'] == contract_id))
        if not contract:
            return json.dumps({"error": f"Contract {contract_id} not found "})

        findings = IP_FINDINGS.get(contract_id,{})
        result={
            "contract_id":contract_id,
            "domain" : "ip_protection",
            "risk_level":findings.get("risk_level","UNKNOWN"),
            "findings":findings.get("findings",[]),
            "concerns":findings.get("concerns",[]),
            "recommendation":findings.get("recommendation",""),

        }
        ip_cache[contract_id] = result 
        return json.dumps(result, indent =2)

    return Agent(
        model=  model,
        system_prompt= system_prompt,
        tools= [review_ip_clauses],
    )
def build_synthesizer_agent() ->Agent:
    """
    Build the Synthesizer Agent using Claude.
    """
    model = BedrockModel(
        model_id = CLAUDE_MODEL,
        region_name = AWS_REGION,
        temperature= 0.2
    )

    system_prompt ="""
        Your are a Synthesizer agent:Your role is ONLY to :
        1. call synthesize_compliance with the contract_id

        2. Request output in exactly 5 lines:
            Overall risk :<HIGH|MEDIUM|LOW>
            Recommendation:<Approve|APPROVE-WITH-CONDITIONS|REJECT>
            Regulatory: <one-line summary>
            Financial :<one-line summary>
            IP Protection :<one-line summary>
        Dont analyse the contract 

    """

    @tool
    def synthesize_compliance(contract_id:str)->str:
        """
        Combine findings from all 3 specialistsinto a compliance recommendation.
        Reads from shared caches populated by te parallel specialist agents.
        Produces: APPROVE , APPROVE-WITH-CONDITIONS, or REJECT.

        Args:
        contract_id : The contract ID(e.g., "CONTRACT-001")

        Returns:
        JSON with unified compliance recommendation
        """

        reg = regulatory_cache.get(contract_id,{})
        fin = financial_cache.get(contract_id,{})
        ip= ip_cache.get(contract_id,{})

        risk_levels ={'HIGH':3,'MEDIUM':2,'LOW':1,'UNKNOWN':0}
        risks=[
            risk_levels.get(reg.get("risk_level","UNKNOWN"), 0),
            risk_levels.get(fin.get("risk_level","UNKNOWN"), 0),
            risk_levels.get(ip.get("risk_level","UNKNOWN"), 0),
        ]

        max_risk = max(risks)
        overall_risk ={3:'HIGH',2:"MEDIUM",1:"LOW"}.get(max_risk,'UNKNOWN')

        high_risk_count = sum(1 for r in risks if r == 3)
        if high_risk_count >= 2:
            recommendation ="REJECT"
        elif high_risk_count==1:
            recommendation='APPROVE-WITH-CONDITIONS'
        elif max_risk == 2:
            recommendation ='APPROVE-WITH-CONDITIONS'
        else:
            recommendation= 'APPROVE'

        result ={
            "contract_id" :contract_id,
            "overall_risk":overall_risk,
            "recommendation": recommendation,
            "regulatory_summary":reg.get("recommendation","No data"),
            "financial_summary":fin.get("recommendation","No data"),
            "ip_summary":ip.get("recommendation","No data"),
            "total_findings":(
                len(reg.get("findings",[]))
                + len(fin.get("findings",[]))
                +len(ip.get("findings",[]))
            ),
            "violations" : reg.get("violations",[]),
            "unfavorable_terms":fin.get("unfavorable_terms",[]),
            "ip_concerns" :ip.get("concerns",[])
        }
        return json.dumps(result, indent =2 )

    return Agent(
        model = model ,
        system_prompt= system_prompt,
        tools =[synthesize_compliance],
    )


# Paralle execution engine

def run_specialists_paralle(contract_id:str)->dict:
    """Run all 3 specialists agents in PARALLE using ThreadPoolExecutor."""

    timings={}

    def run_regulatory():
        agent = build_regulatory_agent()
        t= time.time()
        agent(f"Check regulatory compliance for contract {contract_id} ")
        return time.time() - t
    
    def run_financial():
        agent = build_financial_agent()
        t= time.time()
        agent(f"Assess financial risk for contract {contract_id}")
        return time.time() - t

    def run_ip():
        agent = build_ip_agent()
        t= time.time()
        agent(f"Review ip clauses for contract {contract_id}")
        return time.time() - t

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures ={
            executor.submit(run_regulatory):"regulatory",
            executor.submit(run_financial):"financial",
            executor.submit(run_ip):"ip",
        }
        for future in as_completed(futures):
            name = futures[future]
            timings[name] = future.result()

    return timings


def run_specialists_sequential(contract_id:str)->str:
    """Run all 3 specialists SEQUENTIALLY for comparison"""
    timings ={}

    agent1 = build_regulatory_agent()
    t = time.time()
    agent1(f"Check regulatory compliaance for contract {contract_id}")
    timings["financial"] = time.time() -t

    agent2 = build_financial_agent()
    t = time.time()
    agent2(f"Assess financial risk for contract {contract_id}")
    timings["financial"] = time.time() -t

    agent3 = build_ip_agent()
    t = time.time()
    agent3(f"Review IP clauese or contract {contract_id}")
    timings["ip"] = time.time() - t

    return timings

def main():
    print("=" * 70)
    print(" Parallel Contract Compliance ")
    print("3 Specialist Agents(paralle) + 1 Synthesizer Agent")
    print("="*70)

    comparison =[]

    for contract in CONTRACTS:
        contract_id = contract['id']
        print(f"\n {'-'} *70")
        print(f"Contract : {contract_id} - {contract['title']}")
        print(f"Type :{contract['type']} |Value: ${contract['value']:,} | Duration: {contract['duration_months']}mo")
        print(f"{contract['description'][:65]}...")
        print(f"{'-'*70}")

        regulatory_cache.clear()
        financial_cache.clear()
        ip_cache.clear()

        print(f"\n >>>Runnign 3 specialists in PARALLE ..")
        t_parallel_start = time.time()
        parallel_timings = run_specialists_paralle(contract_id)
        t_specialists = time.time() - t_parallel_start
        print(f" Specialists complete: {t_specialists:.1f}s (parallel)")

        print(f"\n >>> Synthesizer producing compliance report...")
        synthesizer = build_synthesizer_agent()
        t_synth_start = time.time()
        synth_result = synthesizer(f"Synthesize compliance review for contract{contract_id}")
        t_synth = time.time() - t_synth_start
        t_parallel_total = t_specialists +t_synth

        # Read results from caches

        reg = regulatory_cache.get(contract_id,{})
        fin = financial_cache.get(contract_id ,{})
        ip_data = ip_cache.get(contract_id,{})

        # Determine recommendation
        risk_levels ={'HIGH':3,'MEDIUM':2,'LOW':1}
        risks =[
            risk_levels.get(reg.get("risk_level","LOW"),1),
            risk_levels.get(fin.get("risk_level",'MEDIUM'),2),
            risk_levels.get(ip_data.get("risk_level","HIGH"),1),
        ]

        high_count = sum( 1 for r in risks if r==3)
        if high_count >=2:
            decision = 'REJECT'
        elif high_count ==1:
            decision ='APPROVE-WITH-CONDITIONS'
        elif max(risks) ==2:
            decision ="APPROVE-WITH-CONDITIONS"
        else:
            decision ="APPROVE"

        print(f"\n ====Compliance Report ==============")
        print(f"Regulatory :{reg.get('risk_level','?')} - {len(reg.get('violations',[]))} violations found")
        print(f"Financial :{fin.get('risk_level','?')}- {len(fin.get('unfavorable_terms',[]))} unfavorable terms" )
        print(f" IP:         {ip_data.get('risk_level', '?')} — {len(ip_data.get('concerns', []))} concerns")

        print(f" Recommendation: {decision}")
        print(f"  Parallel total: {t_parallel_total:.1f}s (specialists: {t_specialists:.1f}s + synthesizer: {t_synth:.1f}s)")


        # -SEQUENTIAL RUN(for comparison)
        regulatory_cache.clear()
        financial_cache.clear()
        ip_cache.clear()


        print(f"\n >>>Running 3 specialists SEQUENTIALLY ( for comparison)....")

        t_seq_start= time.time()
        sequential_timings = run_specialists_sequential(contract_id)
        t_seq_specialists = time.time() - t_seq_start

        synthesizer2 = build_synthesizer_agent()
        t_synth2_start = time.time()
        synthesizer2(f'Synthesize compliance review for contract {contract_id}')
        t_synth2 = time.time()-t_synth2_start
        t_seq_total = t_seq_specialists + t_synth
        print(f"Sequential total: {t_seq_total:.1f}s")

        if t_parallel_total > 0:
            speedup = t_seq_total /t_parallel_total
            print(f"\n Speedup: {speedup:.1f}x faster with parallel specialists")


        comparison.append({
            "contract":contract_id,
            "type":contract['type'],
            "decision":decision,
            "parallel_s": round(t_parallel_total,1),
            "sequential_s":round(t_seq_total,1),
            "speedup":round(t_seq_total/ t_parallel_total,1) if t_parallel_total > 0 else 0,
        })

        # -----Performance Comparison-------------------

        print(f"\n{'═' * 70}")
        print("  PARALLEL vs SEQUENTIAL — PERFORMANCE COMPARISON")
        print(f"{'═' * 70}")
        print(f"  {'Contract':<15} {'Type':<18} {'Decision':<28} {'Par.':<7} {'Seq.':<7} {'Speed':<6}")
        print(f"  {'─' * 75}")
        for r in comparison:
            print(f"  {r['contract']:<15} {r['type']:<18} {r['decision']:<28} {r['parallel_s']:<7.1f} {r['sequential_s']:<7.1f} {r['speedup']:.1f}x")

        print(f"\n  Key Insight: Parallel analysis turns O(N) sequential reviews")
        print(f"  into O(1) concurrent reviews. Regulatory, financial, and IP")
        print(f"  concerns are orthogonal dimensions — they can be reviewed")
        print(f"  independently. The synthesizer then combines findings into")
        print(f"  a single compliance recommendation.\n")

if __name__== "__main__":
    main()

        






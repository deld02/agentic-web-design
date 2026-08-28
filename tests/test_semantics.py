import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from release_integrity_fixture import add_capability_rows, add_content_lock_fixture, add_release_integrity_fixture
ROOT=Path(__file__).resolve().parents[1]

def run(repo,*args):
    return subprocess.run([sys.executable,*args],cwd=repo,text=True,capture_output=True,encoding='cp1252',errors='replace')

def add_complete_experience_spine(text):
    marker='|---|---|---|---|---|---|---|---|'
    pos=text.find(marker,text.find('## Experience spine'))
    rows=(
        '\n| SCN-001 | Knows the problem but cannot distinguish credible specialists | Why should this approach deserve attention now? | Invisible expertise can be made concrete and comparable | Specific thesis plus an immediate evidence signal | From vague interest to focused relevance | Verify whether the method supports the claim | OPENING |'
        '\n| SCN-002 | Interested but still uncertain about credibility | What proves this is more than positioning language? | The method connects decisions to observable evidence | Ordered method, representative media and bounded claims | From relevance to justified confidence | Decide whether the approach fits the current need | PROOF |'
        '\n| SCN-003 | Understands the approach and has sufficient confidence | What is the sensible next step without overcommitting? | A diagnostic is the smallest useful next action | Clear scope and one direct primary CTA | From confidence to intentional action | Request the diagnostic or end with clarity | ACTION |'
    )
    return text[:pos]+marker+rows+text[pos+len(marker):]

def add_complete_delivery_contract(text):
    empty='DELIVERY_STATUS: NOT_READY\nLANDING_ENTRY:\nRUN_COMMAND:\nBUILD_COMMAND:\nPREVIEW_TARGET:\nDELIVERY_PACKAGE:\nASSET_COMPLETENESS: INCOMPLETE\nLIMITATIONS:\nHANDOFF_SUMMARY:'
    complete='DELIVERY_STATUS: READY\nLANDING_ENTRY: index.html\nRUN_COMMAND: python -m http.server 8000 --directory site-test\nBUILD_COMMAND: NOT_REQUIRED\nPREVIEW_TARGET: site-test/index.html\nDELIVERY_PACKAGE: site-test\nASSET_COMPLETENESS: COMPLETE\nLIMITATIONS: NONE\nHANDOFF_SUMMARY: Complete synthetic landing with integrated representative media and verified responsive behavior.'
    return text.replace(empty,complete)

class SemanticValidationTests(unittest.TestCase):
    def clone(self):
        td=tempfile.TemporaryDirectory(); dst=Path(td.name)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        result=run(dst,'tools/new_project.py','test-project')
        if result.returncode!=0: raise RuntimeError(result.stdout+result.stderr)
        return td,dst

    def mutate_json(self,repo,rel,fn):
        path=repo/rel; data=json.loads(path.read_text(encoding='utf-8')); fn(data)
        path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    def write_decisions(self,repo,rows):
        path=repo/'projects/test-project/decision-log.md'; text=(repo/'templates/project/decision-log.md').read_text(encoding='utf-8')
        text+='\n'+'\n'.join('| '+' | '.join(row)+' |' for row in rows)+'\n'
        path.write_text(text,encoding='utf-8')

    def complete_decision_rows(self):
        return [
            ['PD-001','TECHNOLOGY','Astro selected after comparison with HTML','technology-decision.md#options-compared','06','VERIFIED'],
        ]

    def complete_owner_evidence(self,repo):
        evidence=repo/'projects/test-project/evidence'; evidence.mkdir(exist_ok=True)
        for name in ('ref-direct.png','ref-adjacent.png','ref-frontier.png','ref-simple.png','ref-saturated.png'):
            (evidence/name).write_bytes(b'\x89PNG\r\n\x1a\nsynthetic-reference-capture')
        research=repo/'projects/test-project/research-strategy.md'; text=research.read_text(encoding='utf-8')
        marker='|---|---|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Live website benchmark'))
        rows='\n| Direct example | DIRECT | category search | Clear service thesis and integrated portrait | Strong clarity; conventional rhythm | change | https://example.com/direct | 2026-08-22 | evidence/ref-direct.png |\n| Adjacent example | ADJACENT | editorial search | Cultural authority through pacing | Transferable restraint; different market | adapt | https://example.edu/adjacent | 2026-08-22 | evidence/ref-adjacent.png |\n| Frontier example | FRONTIER | SiteInspire | Editorial asymmetry and material transition | Strong distinction; simplify motion | use | https://example.org/frontier | 2026-08-22 | evidence/ref-frontier.png |\n| Simple example | SIMPLE | Land-book | Restrained typography and one decisive image | Low complexity with strong hierarchy | use | https://example.net/simple | 2026-08-22 | evidence/ref-simple.png |\n| Saturated example | SATURATED | category search | Gradient cards and decorative blobs repeat category clichés | Current but interchangeable | ignore | https://example.io/saturated | 2026-08-22 | evidence/ref-saturated.png |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        text=text.replace(
            'BUSINESS_MODEL:\nPRIMARY_ACTION:\nAUDIENCE_SOPHISTICATION:\nTRUST_REQUIREMENT:\nHUMAN_PRESENCE:\nAUTHORITY_WARMTH_BALANCE:\nTECHNICALITY:\nEXPERIMENTAL_TOLERANCE:\nLOCALITY:\nPROOF_DENSITY:\nNARRATIVE_COMPLEXITY:\nEMOTIONAL_TARGET:\nMOBILE_IMPORTANCE:',
            'BUSINESS_MODEL: expert service sold through a diagnostic conversation\nPRIMARY_ACTION: request a diagnostic\nAUDIENCE_SOPHISTICATION: informed buyers comparing specialist alternatives\nTRUST_REQUIREMENT: high because the service outcome is intangible\nHUMAN_PRESENCE: expert-led without fabricated documentary portraits\nAUTHORITY_WARMTH_BALANCE: authoritative with measured human warmth\nTECHNICALITY: explain method without software-dashboard aesthetics\nEXPERIMENTAL_TOLERANCE: medium in structure and high in authored media\nLOCALITY: locally credible without folkloric visual codes\nPROOF_DENSITY: medium and evidence-led\nNARRATIVE_COMPLEXITY: one thesis with progressive proof\nEMOTIONAL_TARGET: considered confidence and productive tension\nMOBILE_IMPORTANCE: primary acquisition surface with compact visual hierarchy')
        research.write_text(text,encoding='utf-8')
        content=repo/'projects/test-project/content-architecture.md'; text=content.read_text(encoding='utf-8')
        text=text.replace(
            'TEMPLATE_FINGERPRINT:\nPREDICTABLE_SEQUENCE_REMOVED:\nSCENE_RHYTHM_DIFFERENCE:\nHERO_CLICHE_CHALLENGE:\nFINAL_NON_INTERCHANGEABILITY:',
            'TEMPLATE_FINGERPRINT: default hero then three benefits then proof then CTA\nPREDICTABLE_SEQUENCE_REMOVED: evidence becomes an early decision scene instead of a late reassurance block\nSCENE_RHYTHM_DIFFERENCE: thesis compresses into proof, opens into method and resolves in one action\nHERO_CLICHE_CHALLENGE: replaces generic promise plus dashboard with a project-specific decision tension\nFINAL_NON_INTERCHANGEABILITY: the order follows how this buyer verifies invisible expertise')
        text=text.replace('|---|---|---|---|---|','|---|---|---|---|---|\n| Baseline | Hero → problem → proof → CTA | Clear, proof later | Ready after proof | REJECT |\n| Evidence first | Hero → proof → method → CTA | Faster trust | Ready earlier | KEEP |',1)
        marker='|---|---|---|---|---|'
        pos=text.find(marker,text.find('## Sitemap / page or section outline'))
        rows='\n| SCN-001 | Hero | Establish the thesis and invite the next step | Headline, proof signal and primary action | PRIMARY |\n| SCN-002 | Evidence | Make the promise credible | Method, evidence and representative media | PRIMARY |\n| SCN-003 | Closing action | Resolve the decision | Summary and primary CTA | UTILITY |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        text=add_complete_experience_spine(text); text=add_content_lock_fixture(text); text=add_capability_rows(text,(('hallmark-structure-challenger','content-architecture'),))
        content.write_text(text,encoding='utf-8'); visual=repo/'projects/test-project/visual-system.md'; text=visual.read_text(encoding='utf-8')
        marker='|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('## Foundation alternatives and decision evidence'))
        rows='\n| Serif-led | Specific editorial contrast | Holds real copy | Works across scenes | Licensed | KEEP |\n| Sans-led | Familiar category fit | Clear but generic | Works across scenes | Licensed | REJECT |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        marker='|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Content-driven breakpoint evidence'))
        text=text[:pos]+marker+'\n| 320–430 | Mixed headline collides | 382px | Stack accent line | 320–381px |'+text[pos+len(marker):]
        visual.write_text(text,encoding='utf-8')
        creative=repo/'projects/test-project/creative-direction.md'; text=creative.read_text(encoding='utf-8')
        for name in ('artistic-master.png','dir-a.png','dir-b.png','dir-c.png','cmp-direction-a.png','cmp-hero-mobile.png','cmp-body-desktop.png','cmp-body-mobile.png','clr-baseline.png','clr-brand.png','clr-challenger.png','clr-challenge-sheet.png','structural-desktop.png','structural-mobile.png','final-desktop.png','final-mobile.png'):
            (evidence/name).write_bytes(b'\x89PNG\r\n\x1a\nsynthetic-composition')
        text=text.replace(
            'PREMIUM_MEANS_HERE:\nCATEGORY_BASELINE_TO_EXCEED:\nMUST_BE_AUTHORED:\nMUST_AVOID:\nMASTER_MUST_PROVE:\nLANDING_MUST_PRESERVE:',
            'PREMIUM_MEANS_HERE: editorial authority that makes expertise tangible without luxury theatre\nCATEGORY_BASELINE_TO_EXCEED: the clear but interchangeable service landing observed in the direct reference\nMUST_BE_AUTHORED: material imagery, asymmetric evidence composition and typographic contrast\nMUST_AVOID: generic card grids, adjacent stock imagery and fashionable effects without subject meaning\nMASTER_MUST_PROVE: evidence can become an atmospheric material world with recognizable tension\nLANDING_MUST_PRESERVE: the material relationships, reading clarity and authored rhythm across responsive scenes')
        marker='|---|---|---|---|'
        pos=text.find(marker,text.find('## Artistic master'))
        rows='\n| AM-001 | Editorial material world turns evidence into atmosphere and depth | CHATGPT_GENERATE | evidence/artistic-master.png |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        text=text.replace(
            'ARTISTIC_MASTER: AM-___\nSOURCE_DIRECTION: DIR-___\nARTISTIC_INTENT:\nPROJECT_GROUNDS:\nWEB_TRANSLATION_BOUNDARY:',
            'ARTISTIC_MASTER: AM-001\nSOURCE_DIRECTION: DIR-002\nARTISTIC_INTENT: Transform decision signals into a layered editorial material world\nPROJECT_GROUNDS: Research found exchangeability and material process as the visual opportunity\nWEB_TRANSLATION_BOUNDARY: Preserve atmosphere and relationships; never reproduce this as a webpage screenshot')
        marker='|---|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('## Direction divergence'))
        rows='\n| DIR-001 | restrained institutional confidence | humanist sans | centered modular field | documentary paper | flat with precise fades | expert portrait as witness | evidence/dir-a.png |\n| DIR-002 | editorial material authority | expressive serif contrast | asymmetric spatial proof | macro material layers | deep parallax reveal | process as transformation metaphor | evidence/dir-b.png |\n| DIR-003 | technical experimental clarity | grotesk plus mono | radial data composition | translucent scientific plates | orbital responsive motion | no person; signal-field metaphor | evidence/dir-c.png |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        text=text.replace(
            'SELECTED_DIRECTION: DIR-___\nDIRECTION_REVIEW_CHECKPOINT: direction-review\nSELECTION_EVIDENCE:\nREJECTED_DIFFERENCE:',
            'SELECTED_DIRECTION: DIR-002\nDIRECTION_REVIEW_CHECKPOINT: direction-review\nSELECTION_EVIDENCE: isolated review found the strongest match between authority, material proof and distinctive recall\nREJECTED_DIFFERENCE: DIR-001 was too conventional; DIR-003 over-signalled technology')
        text=text.replace(
            'CREATIVE_MASTER: AM-___\nSOURCE_DIRECTION: DIR-___\nVISUAL_THESIS:\nINVARIANTS: TYPE=; COLOR=; COMPOSITION=; MEDIA=; SPACE=; DEPTH=; MOTION=\nFLEX:\nCONTEXTUAL:\nSCENE_GRAMMAR: DOMINANT=; COUNTERPOINT=; TENSION=; SIGNAL=; REST=; TRANSITION=\nSIGNATURE_MECHANISM:\nANTI_RULES:\nDECOMPOSITION_RISKS:',
            'CREATIVE_MASTER: AM-001\nSOURCE_DIRECTION: DIR-002\nVISUAL_THESIS: Editorial evidence makes expertise tangible\nINVARIANTS: TYPE=editorial contrast; COLOR=controlled material palette; COMPOSITION=asymmetric proof; MEDIA=integrated process; SPACE=large narrative pauses; DEPTH=layered evidence; MOTION=reveal construction\nFLEX: crop, scene intensity and proof scale adapt to content density\nCONTEXTUAL: human presence appears only where authentic evidence exists\nSCENE_GRAMMAR: DOMINANT=one authored thesis gesture; COUNTERPOINT=quiet factual structure; TENSION=scale against restraint; SIGNAL=copper decision cue; REST=warm open field; TRANSITION=material motif changes state\nSIGNATURE_MECHANISM: evidence layers assemble into one legible decision field\nANTI_RULES: no generic card grid or adjacent decorative image\nDECOMPOSITION_RISKS: preserve negative space and independent layers')
        text=text.replace(
            'STATUS: PENDING\nPRESENTED_MASTER:\nUSER_SIGNAL:',
            'STATUS: DELEGATED\nPRESENTED_MASTER: AM-001\nUSER_SIGNAL: haz tu propuesta')
        text=add_capability_rows(text,(('anthropic-frontend-design','direction-divergence'),('taste-direction-challenger','direction-divergence'),('anthropic-frontend-design','creative-master'),('taste-direction-challenger','creative-master'))); creative.write_text(text,encoding='utf-8')
        visual=repo/'projects/test-project/visual-system.md'; text=visual.read_text(encoding='utf-8')
        marker='|---|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('## Scene strategy'))
        rows='\n| SCN-001 | Establish thesis with headline, proof and CTA | Expertise feels abstract | Direct split hero with supporting proof | Bespoke layered evidence world assembled through depth, material light and authored reveal | HIGH_VALUE=expertise becomes tangible and memorable; SIMPLIFY=generated depth layers with controlled reveal; EXPENSIVE_NOISE=free-camera WebGL and decorative particles | Generated depth layers with semantic HTML and restrained reveal | Direct translation of material tension from AM-001 |\n| SCN-002 | Make method credible with evidence and representative media | Proof can become a generic card grid | Ordered evidence list with one documentary image | Spatial evidence field where scale and media respond to proof density | HIGH_VALUE=proof gains hierarchy and reading rhythm; SIMPLIFY=layered editorial grid with selective crops; EXPENSIVE_NOISE=continuous scroll choreography on every item | Layered editorial evidence with a deliberate rest zone | Low-intensity translation of material and type relationships |\n| SCN-003 | Resolve decision with summary and primary CTA | Closing can feel like a generic color block | Concise centered CTA | Cinematic return of the master motif with a bespoke transition into the action | HIGH_VALUE=recall reconnects action to the thesis; SIMPLIFY=cropped motif and one transition; EXPENSIVE_NOISE=3D scene built only for the footer | Cropped motif with compact CTA; baseline structure on narrow mobile | Returns to AM-001 without repeating the hero |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        marker='|---|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('## Scene grammar'))
        rows='\n| SCN-001 | oversized thesis | precise proof ledger | atmospheric media against factual copy | copper CTA | open upper field | layered motif opens into paper | full-intensity signature mechanism |\n| SCN-002 | evidence sequence | one material crop | dense facts against large pauses | numbered proof cue | blank reading column | paper field darkens at boundary | quieter grammar with stronger rest |\n| SCN-003 | decisive action | compact service summary | cropped motif against direct CTA | high-contrast action | generous terminal space | master motif resolves and stops | signature returns without hero repetition |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        text=text.replace(
            'CREATIVE_MASTER_SOURCE: AM-___\nINVARIANTS_PRESERVED:\nDELIBERATE_DEVIATIONS:\nHERO_BODY_TRANSLATION:',
            'CREATIVE_MASTER_SOURCE: AM-001\nINVARIANTS_PRESERVED: editorial contrast, asymmetric proof, material layers\nDELIBERATE_DEVIATIONS: mobile stacks media after thesis for reading\nHERO_BODY_TRANSLATION: body reduces intensity while retaining type, material and spacing language')
        text=text.replace(
            'RHYTHM_SEQUENCE:\nPEAKS_AND_RESTS:\nREPETITION_CONTROL:\nHERO_TO_BODY_CONTINUITY:',
            'RHYTHM_SEQUENCE: impact → evidence → rest → resolution\nPEAKS_AND_RESTS: SCN-001 and SCN-003 peak; SCN-002 alternates proof with reading space\nREPETITION_CONTROL: no adjacent scene repeats the same split, scale or media treatment\nHERO_TO_BODY_CONTINUITY: type contrast, material crops and spacing cadence survive at lower intensity')
        marker='|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Color direction territories'))
        composition='LUMINANCE ok; CHROMA ok; TEMPERATURE ok; DOMINANT_ACCENT clear; NEUTRALS controlled; MEDIA compatible; LARGE_SURFACES stable; PERCEPTION distinct'
        rows=f'\n| BASELINE | CLR-001:evidence/clr-baseline.png | dominant 45%; background 30%; foreground 15%; support 7%; accent 3% | direct evidence | {composition} | AA pass | REJECTED |\n| BRAND_LED | CLR-002:evidence/clr-brand.png | dominant 40%; background 32%; foreground 16%; support 8%; accent 4% | identity evidence | {composition} | AA pass | SELECTED |\n| CHALLENGER | CLR-003:evidence/clr-challenger.png | dominant 42%; background 28%; foreground 16%; support 9%; accent 5% | material evidence | {composition} | AA pass | REJECTED |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        marker='|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Scene color map'))
        rows='\n| SCN-001 | Signature thesis, medium density | SIGNATURE: establishes material authority | background=deep ink; foreground=warm white; accent=copper; surface=ink raised | IN=START; OUT=BRIDGE to reading field | copper accent; editorial type | AA text and visible focus pass |\n| SCN-002 | Evidence reading, high density | READING: reduces interference for proof | background=warm paper; foreground=deep ink; accent=copper; surface=soft mineral | IN=BRIDGE from hero; OUT=CUT to closing | copper accent; editorial type | AA text, links and controls pass |\n| SCN-003 | Decision, low density | CONTRAST: restores intensity for action | background=copper; foreground=deep ink; accent=warm white; surface=copper dark | IN=CUT from evidence; OUT=END | editorial type; master crop | AA CTA and focus pass |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        marker='|---|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Scene visual opportunities'))
        rows='\n| HERO | Make expertise tangible | Flat baseline lacks material evidence | EXTERNAL_IMAGE_LOOP | CMP-001:evidence/cmp-direction-a.png | CMP-102:evidence/cmp-hero-mobile.png | HTML/CSS + IMG-001 + FX-001 | Reuse selected direction comp and resolve mobile |\n| BODY_PROOF | Slow down for proof | CSS-only loses documentary texture | EXISTING_MEDIA | CMP-103:evidence/cmp-body-desktop.png | CMP-104:evidence/cmp-body-mobile.png | HTML/CSS + IMG-002 + FX-002 | Editorial crop supports reading |'
        text=text[:pos]+marker+rows+text[pos+len(marker):]
        marker='|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Effect opportunity map'))
        text=text[:pos]+marker+'\n| FX-001 / hero | defining | reveal construction | static/simple/expressive prototypes | layered reveal | desktop.mp4 / mobile.mp4 / reduced.png |'+text[pos+len(marker):]
        marker='|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('### Independent color challenge'))
        text=text[:pos]+marker+'\n| CLR-900:evidence/clr-challenge-sheet.png | hierarchy weakens | identity flattens | becomes interchangeable | selected improves material distinction | PASS |'+text[pos+len(marker):]
        for axis in ('THESIS','TYPOGRAPHIC_VOICE','COLOR_PROVENANCE','COLOR_COMPOSITION','MEDIA_INTEGRATION','MECHANISM_SALIENCE','DEPTH_RHYTHM_DETAIL','DIRECTION_FIDELITY'):
            text=text.replace(f'| {axis} | | | | REVISE |',f'| {axis} | rendered evidence | removal changes the thesis | desktop.png + mobile.png + interaction.mp4 | PASS |')
        text=add_capability_rows(text,(('anthropic-frontend-design','visual-experience'),('jakub-interface-polish','visual-experience'),('jakub-interface-polish','design-review'))); visual.write_text(text,encoding='utf-8')
        technology=repo/'projects/test-project/technology-decision.md'; text=technology.read_text(encoding='utf-8')
        text=text.replace(
            'STRUCTURAL_BUILD_STATUS: PENDING\nIMPLEMENTATION_ROOT:\nSTRUCTURAL_RENDER_DESKTOP:\nSTRUCTURAL_RENDER_MOBILE:',
            'STRUCTURAL_BUILD_STATUS: READY\nIMPLEMENTATION_ROOT: site-test\nSTRUCTURAL_RENDER_DESKTOP: evidence/structural-desktop.png\nSTRUCTURAL_RENDER_MOBILE: evidence/structural-mobile.png')
        technology.write_text(text,encoding='utf-8')
        production=repo/'projects/test-project/production-plan.md'; text=production.read_text(encoding='utf-8')
        text=text.replace('VISUAL_DIAGNOSIS:','VISUAL_DIAGNOSIS: Hero lacks material depth and loses presence beside the thesis',1)
        text=text.replace(
            'ASSET_SET_RATIONALE:\nFLAT_STRETCH_CHECK:\nDUPLICATE_JOB_CHECK:',
            'ASSET_SET_RATIONALE: one hero plate plus authentic proof media covers the distinct visual jobs; the close is a deliberate typographic rest\nFLAT_STRETCH_CHECK: SCN-002 proof media interrupts the longest reading stretch\nDUPLICATE_JOB_CHECK: removed a decorative closing image because it repeated the hero motif')
        narrative_marker='|---|---|---|---|---|---|---|---|---|---|'
        narrative_pos=text.find(narrative_marker,text.find('## Page visual narrative map'))
        narrative_rows=(
            '\n| SCN-001 | ANCHOR | Make expertise tangible | peak before evidence | BACKGROUND | PARALLAX | depth reveals the evidence world as the thesis enters | independent depth layers: background, material field and foreground light | static composed hero on touch and reduced motion | dissolve into proof surface |'
            '\n| SCN-002 | PROOF | Make method credible | medium intensity and slower reading | LATERAL | STATIC | authentic proof must remain beside the claims | one documentary crop | inline crop on mobile | spacing expands into close |'
            '\n| SCN-003 | REST | Resolve the decision without visual noise | low intensity closure | NONE | STATIC | typography and CTA are the intentional terminal rest | semantic HTML and CSS only | same static composition | end |'
        )
        text=text[:narrative_pos]+narrative_marker+narrative_rows+text[narrative_pos+len(narrative_marker):]
        decision_marker='|---|---|---|---|---|---|---|'
        decision_pos=text.find(decision_marker,text.find('## Scene image decisions'))
        decision_rows=(
            '\n| SCN-001 | IMAGE | BACKGROUND | Representative material world | REPRESENTATIVE; no documentary claim | desktop cover; mobile art-directed crop | EXTERNAL:IH-001 |'
            '\n| SCN-002 | IMAGE | LATERAL | Existing proof media | authentic supplied media only | lateral desktop; inline mobile | EXISTING |'
            '\n| SCN-003 | NO_IMAGE | NONE | Typography and CTA carry the close without decorative media | no claim | N/A | NONE |'
        )
        text=text[:decision_pos]+decision_marker+decision_rows+text[decision_pos+len(decision_marker):]
        marker='|---|---|---|---|---|---|---|---|'
        pos=text.find(marker,text.find('## Asset inventory and readiness'))
        text=text[:pos]+marker+'\n| IMG-001 | SCN-001 — Hero is flat beside the main thesis | SCENE_PLATE / REPRESENTATIVE material process | PRIMARY:EXTERNAL_IMAGE_LOOP | FINAL | assets/hero.webp | IH-001 — editorial material scene, wide ratio, copy-safe left area | Hero background layer; cover crop; mobile art-directed crop; slow reveal; static reduced-motion |'+text[pos+len(marker):]
        mechanism='|---|---|---|---|---|---|---|---|---|---|---|---|'
        pos=text.find(mechanism,text.find('### Material effect decisions'))
        text=text[:pos]+mechanism+'\n| FX-001 / hero | defining | static proof | subtle layers | scroll assembly | LIVE_EXECUTION + MECHANISM_LAB | expressive wins | prototype/hero-motion.mp4 | reduced static / 05 | FINAL | index.html#data-fx-hero | LAYERED_2D |'+text[pos+len(mechanism):]
        text=add_capability_rows(text,(('emil-motion-craft','production-plan'),)); production.write_text(text,encoding='utf-8')
        qa=repo/'projects/test-project/qa-release.md'; text=add_complete_delivery_contract(qa.read_text(encoding='utf-8'))
        text=text.replace('FINAL_RENDER_DESKTOP:','FINAL_RENDER_DESKTOP: evidence/final-desktop.png',1)
        text=text.replace('FINAL_RENDER_MOBILE:','FINAL_RENDER_MOBILE: evidence/final-mobile.png',1)
        for axis in ('WHOLE_PAGE_RHYTHM','HERO_TARGET_FIDELITY','EXPERIENCE_CONTINUITY','ASSET_NECESSITY','FORMAT_FIT','MECHANISM_ELIGIBILITY','TRANSITION_CONTINUITY','MOBILE_FALLBACK','TEXT_SPACING_CRAFT'):
            evidence='CMP-001 compared with final desktop and mobile renders' if axis=='HERO_TARGET_FIDELITY' else ('SCN-001, SCN-002 and SCN-003 inspected in final desktop and mobile renders with loaded fonts' if axis=='TEXT_SPACING_CRAFT' else 'desktop and mobile final renders show the intended result'); text=text.replace(f'| {axis} | | | REVISE |',f'| {axis} | {evidence} | no blocking finding / 07 | PASS |')
        text=add_capability_rows(text,(('jakub-interface-polish','build-review'),('vercel-web-interface-guidelines','build-review'))); qa.write_text(text,encoding='utf-8')
        add_release_integrity_fixture(repo,run)
        text=qa.read_text(encoding='utf-8').replace(
            'BACKGROUND_CHARACTER:\nACCENT_CHARACTER:\nDISPLAY_TYPE_CHARACTER:\nHERO_COMPOSITION:\nHERO_MEDIA:\nSIGNATURE_MECHANISM:\nDEPTH_MEDIUM:\nMOTION_INTENSITY:',
            'BACKGROUND_CHARACTER: warm paper alternating with deep material ink\nACCENT_CHARACTER: sparse copper decision signal\nDISPLAY_TYPE_CHARACTER: high-contrast editorial serif against factual sans\nHERO_COMPOSITION: asymmetric thesis and evidence field\nHERO_MEDIA: representative layered material scene\nSIGNATURE_MECHANISM: evidence layers assemble into a decision field\nDEPTH_MEDIUM: layered 2D media with restrained parallax\nMOTION_INTENSITY: one defining reveal with quiet body motion')
        qa.write_text(text,encoding='utf-8')

    def test_clean_repo_passes(self):
        result=run(ROOT,'tools/validate_system.py')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_progressive_intake_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/progressive-intake.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/progressive-intake.md',result.stdout)
        finally: td.cleanup()

    def test_bounded_execution_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/bounded-execution.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/bounded-execution.md',result.stdout)
        finally: td.cleanup()

    def test_operational_runtime_skill_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'skills/agentic-web-design/SKILL.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('skills/agentic-web-design/SKILL.md',result.stdout)
        finally: td.cleanup()

    def test_typography_spacing_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/typography-spacing.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/typography-spacing.md',result.stdout)
        finally: td.cleanup()

    def test_image_decision_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/image-decisions.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/image-decisions.md',result.stdout)
        finally: td.cleanup()

    def test_g4_cannot_approve_without_final_or_reviewed_mechanism(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(content_model='static'))
            def change(d):
                d['gates']['G4'].update(status='APPROVED',evidence=['production-plan.md','technology-decision.md','qa-release.md'],blockers=[],last_decision='production approved')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('requires a reviewed material mechanism decision',result.stdout)
        finally: td.cleanup()

    def test_g4_cannot_approve_without_final_visual_asset(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(content_model='static'))
            def change(d):
                d['gates']['G4'].update(status='APPROVED',evidence=['production-plan.md','technology-decision.md','qa-release.md'],blockers=[],last_decision='production approved')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('requires at least one scene-bearing PRIMARY FINAL IMG asset',result.stdout)
        finally: td.cleanup()

    def test_scene_color_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/scene-color-system.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/scene-color-system.md',result.stdout)
        finally: td.cleanup()

    def test_effect_selection_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/effect-selection.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/effect-selection.md',result.stdout)
        finally: td.cleanup()

    def test_material_decision_method_is_required(self):
        td,repo=self.clone()
        try:
            (repo/'docs/methods/material-decisions.md').unlink()
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('docs/methods/material-decisions.md',result.stdout)
        finally: td.cleanup()

    def test_g1_approval_requires_narrative_decision(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(project_type='landing'))
            def change(d):
                d['gates']['G0'].update(status='APPROVED',evidence=['PROJECT.md','project.config.json','brief.md'],blockers=[],last_decision='defined')
                d['checkpoints']['research-strategy'].update(status='APPROVED',evidence=['research-strategy.md'],blockers=[],last_decision='researched')
                d['gates']['G1'].update(status='APPROVED',evidence=['research-strategy.md','content-architecture.md'],blockers=[],last_decision='structured')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('must compare at least two narrative alternatives',result.stdout)
        finally: td.cleanup()

    def test_single_unchallenged_option_cannot_close_material_decision(self):
        td,repo=self.clone()
        try:
            path=repo/'projects/test-project/content-architecture.md'; text=path.read_text(encoding='utf-8')
            text=text.replace('|---|---|---|---|---|','|---|---|---|---|---|\n| Only flow | Hero → CTA | Fast | Immediate | KEEP |',1); path.write_text(text,encoding='utf-8')
            def change(d): d['gates']['G1'].update(status='APPROVED',evidence=['research-strategy.md','content-architecture.md'],blockers=[],last_decision='single flow')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('must compare at least two narrative alternatives',result.stdout)
        finally: td.cleanup()

    def test_responsive_rule_requires_observed_failure(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(visual_identity_mode='establish'))
            def change(d): d['gates']['G3'].update(status='APPROVED',evidence=['visual-system.md'],blockers=[],last_decision='visual approved')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('needs observed responsive failure/recomposition evidence',result.stdout)
        finally: td.cleanup()

    def test_approved_without_evidence_fails(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/status.json',lambda d:d['gates']['G0'].update(status='APPROVED',evidence=[],last_decision='approved'))
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('APPROVED without evidence',result.stdout)
        finally: td.cleanup()

    def test_unsatisfied_entry_condition_fails(self):
        td,repo=self.clone()
        try:
            def change(d):
                d['gates']['G0']['status']='PENDING'; d['gates']['G1']['status']='ACTIVE'
                d.update(active_stage='content-architecture',active_gate='G1',active_agent='02',active_mode='content-architecture',status='ACTIVE')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('entry conditions not met',result.stdout)
        finally: td.cleanup()

    def test_schema_rejects_unknown_field(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/status.json',lambda d:d.update(typo_field=True))
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('schema validation failed',result.stdout)
        finally: td.cleanup()

    def test_agent_audit_fails_closed(self):
        td,repo=self.clone()
        try:
            path=repo/'agents/04-visual-ui-design.md'
            path.write_text(path.read_text(encoding='utf-8').replace('## MISIÓN','## MISION_BROKEN',1),encoding='utf-8')
            result=run(repo,'tools/audit_agents.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('problems',result.stdout)
        finally: td.cleanup()

    def test_direction_review_is_mandatory(self):
        td,repo=self.clone()
        try:
            def change(d): next(x for x in d['gates'] if x['id']=='G2')['approval_requires_stages']=[]
            self.mutate_json(repo,'config/gates.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('missing mandatory core checkpoint direction-review',result.stdout)
        finally: td.cleanup()

    def test_technology_selection_is_mandatory(self):
        td,repo=self.clone()
        try:
            def change(d): next(x for x in d['gates'] if x['id']=='G4')['approval_requires_stages'].remove('technology-selection')
            self.mutate_json(repo,'config/gates.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('missing mandatory core checkpoint technology-selection',result.stdout)
        finally: td.cleanup()

    def test_g0_requires_defined_project_context(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(project_type='undetermined'))
            def change(d):
                d['gates']['G0'].update(status='APPROVED',evidence=['PROJECT.md','project.config.json','brief.md'],blockers=[],last_decision='synthetic')
                d['status']='PENDING'
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('project_type undetermined',result.stdout)
        finally: td.cleanup()

    def test_technology_approval_requires_selected_choice(self):
        td,repo=self.clone()
        try:
            def change(d):
                c=d['checkpoints']['technology-selection']; c.update(status='APPROVED',evidence=['technology-decision.md'],blockers=[],last_decision='selected')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('without selected technology',result.stdout)
        finally: td.cleanup()

    def test_dag_edge_requires_semantic_condition(self):
        td,repo=self.clone()
        try:
            def change(d): next(x for x in d['stages'] if x['id']=='content-architecture')['entry_requires']['checkpoints']={}
            self.mutate_json(repo,'config/pipeline.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('lacks APPROVED semantic entry condition',result.stdout)
        finally: td.cleanup()

    def test_render_driven_critical_pipeline_order_is_mandatory(self):
        td,repo=self.clone()
        try:
            def change(d):
                stage=next(x for x in d['stages'] if x['id']=='production-plan')
                stage['depends_on']=['design-review']
                stage['entry_requires']={'gates':{'G3':['APPROVED']},'checkpoints':{'design-review':['APPROVED']}}
            self.mutate_json(repo,'config/pipeline.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('critical pipeline order mismatch',result.stdout)
        finally: td.cleanup()

    def test_github_actions_must_be_sha_pinned(self):
        td,repo=self.clone()
        try:
            path=repo/'.github/workflows/validate-agent-system.yml'
            path.write_text(path.read_text(encoding='utf-8').replace('actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1','actions/checkout@v7'),encoding='utf-8')
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('not pinned to a full commit SHA',result.stdout)
        finally: td.cleanup()

    def test_non_landing_project_type_is_rejected(self):
        td,repo=self.clone()
        try:
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(project_type='commerce'))
            result=run(repo,'tools/validate_system.py')
            self.assertNotEqual(result.returncode,0); self.assertIn('invalid project_type',result.stdout)
        finally: td.cleanup()

    def test_new_project_is_valid_and_minimal(self):
        td,repo=self.clone()
        try:
            result=run(repo,'tools/new_project.py','demo-site')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(len(list((repo/'projects/demo-site').iterdir())),12)
            result=run(repo,'tools/validate_system.py')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        finally: td.cleanup()

    def test_fully_approved_release_state_passes(self):
        td,repo=self.clone()
        try:
            config=repo/'projects/test-project/project.config.json'; cd=json.loads(config.read_text(encoding='utf-8'))
            cd.update(project_type='landing',visual_identity_mode='establish',content_model='static',implementation_root='site-test'); cd['technology']={'status':'selected','choice':'astro','decision_artifact':'technology-decision.md'}
            config.write_text(json.dumps(cd,indent=2)+'\n',encoding='utf-8')
            site=repo/'site-test'; (site/'assets').mkdir(parents=True)
            (site/'assets/hero.webp').write_bytes(b'RIFFxxxxWEBPsynthetic-visual')
            (site/'index.html').write_text('<style>[data-fx-hero]{transition:transform .3s ease}</style><main data-fx-hero><h1>Invisible expertise, made concrete</h1><img src="assets/hero.webp" alt="Synthetic visual"><a>Request the diagnostic</a></main>',encoding='utf-8')
            for path in (repo/'projects/test-project').glob('*.md'):
                text=path.read_text(encoding='utf-8').replace('Status: PENDING','Status: COMPLETE').replace('Status: UNDETERMINED','Status: SELECTED')
                if len(text.strip())<80: text+='\nVerified synthetic lifecycle evidence.\n'*3
                path.write_text(text,encoding='utf-8')
            qa=repo/'projects/test-project/qa-release.md'; text=qa.read_text(encoding='utf-8')
            for area in ('Objective and action','Content and assets','Visual direction','Responsive composition','Interaction and motion','Build fidelity','Functional delivery','Accessibility and performance'):
                text=text.replace(f'| {area} | PENDING | |',f'| {area} | COMPLETE | synthetic owner |')
            text+='\n| E-1 | synthetic | journey | pass | fixture | 2026-08-20 | test | COMPLETE | synthetic |\n'
            text+='| E-2 | synthetic | accessibility | pass | fixture | 2026-08-20 | test | COMPLETE | synthetic |\n'
            text+='| E-3 | synthetic | performance | pass | fixture | 2026-08-20 | test | COMPLETE | synthetic |\n'
            qa.write_text(text,encoding='utf-8')
            self.complete_owner_evidence(repo)
            self.write_decisions(repo,self.complete_decision_rows())
            gates=json.loads((repo/'config/gates.json').read_text(encoding='utf-8'))['gates']
            def change(d):
                for gdef in gates:
                    g=d['gates'][gdef['id']]; g.update(status='APPROVED',evidence=gdef['required_artifacts'] or ['decision-log.md'],blockers=[],last_decision='synthetic approval')
                for cid,c in d['checkpoints'].items():
                    c.update(status='APPROVED',evidence=['synthetic'],blockers=[],last_decision='synthetic approval')
                    if cid in {'direction-review','design-review','build-review'}: c['review_context']='ISOLATED'
                d.update(active_stage='release',active_gate='G5',active_agent='00',active_mode='release',status='APPROVED')
                d['release']={'eligible':True,'reason':'all prerequisites approved'}
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/validate_system.py')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        finally: td.cleanup()

    def test_independent_review_requires_isolated_context(self):
        td,repo=self.clone()
        try:
            def change(d):
                item=d['checkpoints']['direction-review']
                item.update(status='APPROVED',evidence=['creative-direction.md'],blockers=[],last_decision='approved',review_context='PENDING')
            self.mutate_json(repo,'projects/test-project/status.json',change)
            result=run(repo,'tools/audit_state.py','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('APPROVED without ISOLATED',result.stdout)
        finally: td.cleanup()

    def test_gate_preflight_blocks_unfilled_g1(self):
        td,repo=self.clone()
        try:
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('G1 requires at least two narrative alternatives',result.stdout)
        finally: td.cleanup()

    def test_g5_blocks_not_ready_final_delivery_contract(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/qa-release.md'
            path.write_text(path.read_text(encoding='utf-8').replace('DELIVERY_STATUS: READY','DELIVERY_STATUS: NOT_READY',1),encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G5','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('final delivery is NOT_READY',result.stdout)
        finally: td.cleanup()

    def test_g5_requires_final_hero_comparison_with_approved_cmp(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/qa-release.md'; text=path.read_text(encoding='utf-8')
            path.write_text(text.replace('CMP-001 compared with final desktop and mobile renders','final desktop and mobile renders look consistent',1),encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G5','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('HERO_TARGET_FIDELITY must compare the approved CMP-*',result.stdout)
        finally: td.cleanup()
    def test_g1_requires_current_balanced_reference_captures(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            (repo/'projects/test-project/evidence/ref-frontier.png').unlink()
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('reference benchmark Frontier example composition evidence is missing or invalid',result.stdout)
        finally: td.cleanup()

    def test_g1_rejects_stale_visual_calibration(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/research-strategy.md'
            path.write_text(path.read_text(encoding='utf-8').replace('2026-08-22','2025-01-01',1),encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('reference benchmark Direct example is stale',result.stdout)
        finally: td.cleanup()

    def test_g1_requires_primary_scene_outline(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/content-architecture.md'
            text=path.read_text(encoding='utf-8').replace(' | PRIMARY |',' | UTILITY |')
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('requires at least one PRIMARY scene',result.stdout)
        finally: td.cleanup()

    def test_quantitative_claim_cannot_remain_unclassified(self):
        td,repo=self.clone()
        try:
            path=repo/'projects/test-project/content-architecture.md'
            text=path.read_text(encoding='utf-8').replace('## Content and copy\n','## Content and copy\n\nMás de 20 clientes atendidos.\n',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Claim ledger is empty',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_rendered_hero_stress_pass(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            path=repo/'projects/test-project/visual-system.md'
            text=path.read_text(encoding='utf-8').replace(
                '| THESIS | rendered evidence | removal changes the thesis | desktop.png + mobile.png + interaction.mp4 | PASS |',
                '| THESIS | rendered evidence | removal changes the thesis | desktop.png + mobile.png + interaction.mp4 | REVISE |',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('THESIS is not PASS',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_strategy_for_every_primary_scene(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            lines=path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(line for line in lines if not line.startswith('| SCN-002 |'))+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing Scene Strategy for scene SCN-002',result.stdout)
        finally: td.cleanup()

    def test_g3_high_value_challenge_also_covers_utility_scene(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            lines=path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(
                line for line in lines
                if not line.startswith('| SCN-003 | Resolve decision with summary and primary CTA')
            )+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing Scene Strategy for scene SCN-003',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_global_page_rhythm(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            text=path.read_text(encoding='utf-8').replace(
                'PEAKS_AND_RESTS: SCN-001 and SCN-003 peak; SCN-002 alternates proof with reading space',
                'PEAKS_AND_RESTS:',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('global page rhythm missing PEAKS_AND_RESTS',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_color_assignment_for_every_scene(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            lines=path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(line for line in lines if not line.startswith('| SCN-003 | Decision, low density'))+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing color assignment for scene SCN-003',result.stdout)
        finally: td.cleanup()

    def test_g3_rejects_abstract_scene_color_mode_without_roles(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            text=path.read_text(encoding='utf-8').replace(
                'background=warm paper; foreground=deep ink; accent=copper; surface=soft mineral',
                'READING palette',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('SCN-002 color roles missing concrete background assignment',result.stdout)
            self.assertIn('SCN-002 color roles missing concrete foreground assignment',result.stdout)
        finally: td.cleanup()

    def test_g2_requires_physical_artistic_master(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            (repo/'projects/test-project/evidence/artistic-master.png').unlink()
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('composition evidence is missing or invalid',result.stdout)
        finally: td.cleanup()

    def test_g2_quality_bar_must_precede_artistic_master(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8')
            start=text.index('## Project-specific quality bar')
            end=text.index('## Artistic master',start)
            block=text[start:end]
            text=text[:start]+text[end:]
            insert=text.index('## Artistic master confirmation')
            text=text[:insert]+block+text[insert:]
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('quality bar must appear before the artistic master',result.stdout)
        finally: td.cleanup()

    def test_g2_quality_bar_rejects_generic_premium_label(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace(
                'PREMIUM_MEANS_HERE: editorial authority that makes expertise tangible without luxury theatre',
                'PREMIUM_MEANS_HERE: premium moderno elegante',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('PREMIUM_MEANS_HERE is only a generic quality label',result.stdout)
        finally: td.cleanup()

    def test_material_g2_requires_selected_creative_master_handoff(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace('CREATIVE_MASTER: AM-001','CREATIVE_MASTER: AM-999',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('creative master AM-999 must match exactly one artistic master',result.stdout)
        finally: td.cleanup()

    def test_g2_requires_artistic_master_before_web_design(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace('ARTISTIC_MASTER: AM-001','ARTISTIC_MASTER:',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('requires ARTISTIC_MASTER',result.stdout)
        finally: td.cleanup()

    def test_g2_artistic_master_requires_actual_image_generation(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace(
                '| AM-001 | Editorial material world turns evidence into atmosphere and depth | CHATGPT_GENERATE |',
                '| AM-001 | Editorial material world turns evidence into atmosphere and depth | HTML_PROTOTYPE |',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('must use CHATGPT_GENERATE',result.stdout)
        finally: td.cleanup()

    def test_g2_rejects_multiple_artistic_masters(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace(
                '| AM-001 | Editorial material world turns evidence into atmosphere and depth | CHATGPT_GENERATE | evidence/artistic-master.png |',
                '| AM-001 | Editorial material world turns evidence into atmosphere and depth | CHATGPT_GENERATE | evidence/artistic-master.png |\n| AM-002 | Duplicate tournament direction | CHATGPT_GENERATE | evidence/artistic-master.png |',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('requires exactly one artistic master evidence row',result.stdout)
        finally: td.cleanup()

    def test_g4_external_image_requires_exact_integration(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/production-plan.md'
            text=path.read_text(encoding='utf-8').replace(
                '| Hero background layer; cover crop; mobile art-directed crop; slow reveal; static reduced-motion |',
                '| |',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing exact landing integration',result.stdout)
        finally: td.cleanup()

    def test_g4_image_production_requires_structural_renders(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/technology-decision.md'
            text=path.read_text(encoding='utf-8').replace(
                'STRUCTURAL_RENDER_DESKTOP: evidence/structural-desktop.png',
                'STRUCTURAL_RENDER_DESKTOP:',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('requires STRUCTURAL_RENDER_DESKTOP',result.stdout)
        finally: td.cleanup()

    def test_g4_external_image_requires_web_ready_output_type(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/production-plan.md'
            text=path.read_text(encoding='utf-8').replace(
                'SCENE_PLATE / REPRESENTATIVE material process',
                'generic nice image',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('no valid web-ready production type',result.stdout)
        finally: td.cleanup()

    def test_g4_requires_image_decision_for_every_scene(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/production-plan.md'
            lines=path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(line for line in lines if not line.startswith('| SCN-003 | NO_IMAGE |'))+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('missing image decision for scene SCN-003',result.stdout)
        finally: td.cleanup()

    def test_g4_requires_physical_final_desktop_and_mobile_renders(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            (repo/'projects/test-project/evidence/final-mobile.png').unlink()
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('final mobile render composition evidence is missing or invalid',result.stdout)
        finally: td.cleanup()

    def test_g2_blocks_while_visual_confirmation_is_pending(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace('STATUS: DELEGATED','STATUS: PENDING',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('artistic master confirmation is PENDING',result.stdout)
        finally: td.cleanup()

    def test_g2_confirmation_must_present_artistic_master(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            text=path.read_text(encoding='utf-8').replace('PRESENTED_MASTER: AM-001','PRESENTED_MASTER: AM-002',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('confirmation must present the artistic master',result.stdout)
        finally: td.cleanup()

    def test_material_g3_requires_fidelity_to_selected_creative_master(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            text=path.read_text(encoding='utf-8').replace('CREATIVE_MASTER_SOURCE: AM-001','CREATIVE_MASTER_SOURCE: AM-002',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('creative master source AM-002 does not match selected AM-001',result.stdout)
        finally: td.cleanup()

    def test_material_g3_requires_body_scene_decomposition(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(delivery_profile='standard'))
            path=repo/'projects/test-project/visual-system.md'
            text=path.read_text(encoding='utf-8').replace('HTML/CSS + IMG-002 + FX-002','flat screenshot',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('lacks HTML/CSS + IMG-* + FX-* decomposition',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_physical_color_territory_evidence(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            (repo/'projects/test-project/evidence/clr-challenger.png').unlink()
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('CLR-003 composition evidence is missing or invalid',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_color_composition_axis_and_independent_challenge(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            text=path.read_text(encoding='utf-8').replace(
                '| COLOR_COMPOSITION | rendered evidence | removal changes the thesis | desktop.png + mobile.png + interaction.mp4 | PASS |',
                '| COLOR_COMPOSITION | rendered evidence | removal changes the thesis | desktop.png + mobile.png + interaction.mp4 | REVISE |',1).replace(
                '| CLR-900:evidence/clr-challenge-sheet.png | hierarchy weakens | identity flattens | becomes interchangeable | selected improves material distinction | PASS |',
                '| CLR-900:evidence/clr-challenge-sheet.png | hierarchy weakens | identity flattens | becomes interchangeable | selected improves material distinction | REVISE |',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('COLOR_COMPOSITION is not PASS',result.stdout)
            self.assertIn('independent color challenge is not PASS',result.stdout)
        finally: td.cleanup()

    def test_focused_material_reuses_hero_without_mandatory_body_comp(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            self.mutate_json(repo,'projects/test-project/project.config.json',lambda d:d.update(delivery_profile='focused'))
            path=repo/'projects/test-project/visual-system.md'
            lines=path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(line for line in lines if not line.startswith('| BODY_PROOF |'))+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        finally: td.cleanup()

    def test_g1_requires_compiled_project_context(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/research-strategy.md'
            path.write_text(path.read_text(encoding='utf-8').replace('BUSINESS_MODEL: expert service sold through a diagnostic conversation','BUSINESS_MODEL:',1),encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('context compiler missing BUSINESS_MODEL',result.stdout)
        finally: td.cleanup()

    def test_g1_requires_structural_interchangeability_challenge(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/content-architecture.md'
            path.write_text(path.read_text(encoding='utf-8').replace('TEMPLATE_FINGERPRINT: default hero then three benefits then proof then CTA','TEMPLATE_FINGERPRINT:',1),encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('structural challenge missing TEMPLATE_FINGERPRINT',result.stdout)
        finally: td.cleanup()

    def test_g1_requires_saturated_code_reference(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/research-strategy.md'
            lines=[line for line in path.read_text(encoding='utf-8').splitlines() if '| SATURATED |' not in line]
            path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G1','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('saturated-code reference',result.stdout)
        finally: td.cleanup()

    def test_g2_requires_three_direction_boards(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'
            lines=[line for line in path.read_text(encoding='utf-8').splitlines() if not line.startswith('| DIR-003 |')]
            path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('exactly three divergent direction territories',result.stdout)
        finally: td.cleanup()

    def test_g2_requires_approved_isolated_direction_review(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('approved direction-divergence checkpoint',result.stdout)
            self.assertIn('approved isolated direction-review checkpoint',result.stdout)
        finally: td.cleanup()

    def test_g2_rejects_convergent_directions(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/creative-direction.md'; text=path.read_text(encoding='utf-8')
            text=text.replace('| DIR-003 | technical experimental clarity | grotesk plus mono | radial data composition | translucent scientific plates | orbital responsive motion | no person; signal-field metaphor | evidence/dir-c.png |','| DIR-003 | editorial material authority | expressive serif contrast | asymmetric spatial proof | macro material layers | orbital responsive motion | no person; signal-field metaphor | evidence/dir-c.png |',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G2','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('four are required',result.stdout)
        finally: td.cleanup()

    def test_g3_requires_scene_grammar_for_every_scene(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/visual-system.md'
            lines=[line for line in path.read_text(encoding='utf-8').splitlines() if not line.startswith('| SCN-002 | evidence sequence |')]
            path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G3','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('missing Scene Grammar for scene SCN-002',result.stdout)
        finally: td.cleanup()

    def test_g5_requires_design_fingerprint(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/qa-release.md'
            path.write_text(path.read_text(encoding='utf-8').replace('HERO_COMPOSITION: asymmetric thesis and evidence field','HERO_COMPOSITION:',1),encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G5','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('design fingerprint missing HERO_COMPOSITION',result.stdout)
        finally: td.cleanup()

    def test_g4_requires_page_level_visual_narrative_for_every_scene(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/production-plan.md'
            lines=[line for line in path.read_text(encoding='utf-8').splitlines() if not line.startswith('| SCN-002 | PROOF |')]
            path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('missing page visual narrative for scene SCN-002',result.stdout)
        finally: td.cleanup()

    def test_g4_parallax_requires_independent_depth_layers(self):
        td,repo=self.clone()
        try:
            self.complete_owner_evidence(repo)
            path=repo/'projects/test-project/production-plan.md'; text=path.read_text(encoding='utf-8')
            text=text.replace('independent depth layers: background, material field and foreground light','one flat hero photograph',1)
            path.write_text(text,encoding='utf-8')
            result=run(repo,'tools/validate_gate.py','G4','--project-dir','projects/test-project')
            self.assertNotEqual(result.returncode,0); self.assertIn('PARALLAX requires independent depth layers',result.stdout)
        finally: td.cleanup()

    def test_skill_fails_closed_without_managed_harness_context(self):
        text=(ROOT/'skills/agentic-web-design/SKILL.md').read_text(encoding='utf-8')
        for token in ('Execution lock', 'MANAGED', 'UNMANAGED', 'HARNESS_RUN_DIR', 'must not build HTML'):
            self.assertIn(token,text)

    def test_chatgpt_entrypoint_forbids_manual_pipeline_fallback(self):
        text=(ROOT/'CHATGPT-PROJECT-INSTRUCTIONS.md').read_text(encoding='utf-8')
        for token in ('HARNESS_STAGE', 'UNMANAGED', 'must stop before', 'unacceptable fallback', 'IMAGE_GEN', 'chat-next'):
            self.assertIn(token,text)

if __name__=='__main__': unittest.main()

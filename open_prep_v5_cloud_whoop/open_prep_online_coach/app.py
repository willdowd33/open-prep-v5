import os
import json
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse, JSONResponse, Response
from openai import OpenAI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

app = FastAPI(title="Open Prep Coach", version="5.0.0")

@app.middleware("http")
async def disable_stale_page_cache(request, call_next):
    response = await call_next(request)
    if request.url.path in ("/", "/index.html", "/api/version", "/manifest.webmanifest", "/service-worker.js"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response

@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(ROOT / "manifest.webmanifest", media_type="application/manifest+json")

@app.get("/icon.svg")
def icon():
    return FileResponse(ROOT / "icon.svg", media_type="image/svg+xml")

@app.get("/service-worker.js")
def service_worker():
    return FileResponse(ROOT / "service-worker.js", media_type="application/javascript")


class NutritionRequest(BaseModel):
    description: str = Field(min_length=2, max_length=3000)

class CoachRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=12)
    athlete_profile: dict[str, Any] = Field(default_factory=dict)
    current_session: dict[str, Any] = Field(default_factory=dict)

COACH_INSTRUCTIONS = """
You are Open Prep Coach, an evidence-informed CrossFit, strength, Olympic lifting,
and running training assistant for one athlete preparing for a CrossFit Open-style
competition. Be practical, direct, supportive, and specific. Use the athlete's
provided training maxes, current session, and recent logs when relevant.

Athlete profile currently supplied:
- Back squat 335 lb; front squat 305 lb; deadlift 445 lb; bench 290 lb.
- Clean & jerk 280 lb; snatch 225 lb; strict press 170 lb.
- 40 unbroken chest-to-bar pull-ups.
- Half marathon 1:58:34; estimated 5K about 21:00.
- Recent running base 20–30 miles/week.
- Reported symptoms: left QL overactivity, right hip/glute med/TFL concerns,
  right lateral knee/IT-band-region pain, and left shoulder/elbow symptoms.
These are user-reported descriptions, not confirmed diagnoses or proof of a
single kinetic-chain cause.

Coaching rules:
1. Interpret loads as training context, not proof of readiness. Avoid prescribing
   frequent max attempts. Most work should be technically sound and autoregulated.
2. Manage total stress across CrossFit, lifting, and running. Do not add volume
   automatically; compare against recent logs and the athlete's established base.
3. Give clear scaling/substitution options when fatigue or symptoms warrant them.
4. Never diagnose an injury, claim a muscle is "failing" based only on symptoms,
   or present a rehab protocol as a substitute for an in-person assessment.
5. For pain that escalates, changes mechanics, persists/worsens after training,
   or is accompanied by new/progressive weakness, numbness, swelling, locking,
   or giving-way, advise stopping the provoking activity and getting assessed by
   an appropriate clinician. New/progressive neurological symptoms or major
   weakness warrant prompt medical attention.
6. Keep advice concise but useful. If asked to review a session, state what went
   well, concerns, and one or two concrete next-session adjustments.
7. Do not pretend to have sensor/video access or live monitoring. You only see
   the data sent with the current request.
8. When the user explicitly asks to add, remove or modify workout programming,
   propose concrete changes to the selected workout only. Do not claim changes
   were saved; the app asks the user to review and approve them.
"""

@app.get("/")
def home():
    return FileResponse(ROOT / "index.html", headers={"Cache-Control":"no-store, max-age=0", "Pragma":"no-cache"})

@app.get("/nutrition_core.js")
def nutrition_core_script():
    return FileResponse(ROOT / "nutrition_core.js", media_type="application/javascript", headers={"Cache-Control":"no-store"})

@app.get("/api/version")
def app_version():
    return {"version":"5.0","hosting":"render-ready"}

@app.get("/api/health")
def health():
    return {"status": "ok", "configured": bool(os.getenv("OPENAI_API_KEY"))}

async def verified_user(authorization: str | None = Header(default=None)):
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise HTTPException(503, "Configure SUPABASE_URL and SUPABASE_ANON_KEY on Render for V5 AI and WHOOP features.")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in to Supabase first.")
    async with httpx.AsyncClient(timeout=12) as http:
        r = await http.get(url+"/auth/v1/user", headers={"apikey":key,"Authorization":authorization})
    if r.status_code != 200 or not r.json().get("id"):
        raise HTTPException(401, "Supabase session expired. Sign in again.")
    return r.json()["id"]


@app.post("/api/coach")
def coach(payload: CoachRequest, user=Depends(verified_user)):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is missing. Add it to the .env file and restart Open Prep.")
    model = os.getenv("OPENAI_MODEL", "gpt-5.5")
    client = OpenAI(api_key=api_key)
    context = (
        "ATHLETE PROFILE AND RECENT TRAINING DATA (user-provided):\n"
        + str(payload.athlete_profile)
        + "\n\nCURRENT SELECTED SESSION AND LOG:\n"
        + str(payload.current_session)
        + "\n\nUSER MESSAGE:\n"
        + payload.message
    )
    conversation = []
    for item in payload.history[-12:]:
        role = item.get("role")
        content = item.get("content", "")
        if role in ("user", "assistant") and isinstance(content, str):
            conversation.append({"role": role, "content": content[:5000]})
    conversation.append({"role": "user", "content": context})
    edit_requested = bool(re.search(r"\b(add|edit|change|modify|replace|swap|remove|adjust|rewrite|update)\b", payload.message, re.I)) and bool(re.search(r"\b(workout|session|program|strength|skill|wod|metcon|run|rehab|exercise|lift|sets|reps)\b", payload.message, re.I))
    if edit_requested:
        instructions = COACH_INSTRUCTIONS + """
Return ONLY a JSON object with keys:
answer: concise coaching explanation;
workout_update: object with any of these keys: strength, skill, wod, run, rehab.
Each updated field MUST contain the COMPLETE replacement text for that section,
not just a fragment. Preserve other sections by omitting their keys. Never change
unrequested fields. The user will approve before saving. No markdown fences.
"""
    else:
        instructions = COACH_INSTRUCTIONS
    try:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=conversation,
            max_output_tokens=900,
        )
        raw = response.output_text
        if edit_requested:
            try:
                parsed = json.loads(raw)
                updates = parsed.get("workout_update") or {}
                valid = {k: v[:8000] for k, v in updates.items() if k in ("strength", "skill", "wod", "run", "rehab") and isinstance(v, str)} if isinstance(updates, dict) else {}
                return {"answer": str(parsed.get("answer", "Review the proposed workout changes.")), "workout_update": valid or None, "model": model}
            except (ValueError, AttributeError, TypeError):
                return {"answer": raw + "\n\nI couldn't format a safe workout update. No changes were applied.", "model": model}
        return {"answer": raw, "model": model}
    except Exception as exc:
        # Do not expose secrets or raw provider internals to the browser.
        raise HTTPException(status_code=502, detail=f"AI provider request failed ({type(exc).__name__}). Check API access, model setting, and billing.")


class NutritionCoachRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2500)
    goals: dict[str, Any] = Field(default_factory=dict)
    totals: dict[str, Any] = Field(default_factory=dict)
    activity: dict[str, Any] = Field(default_factory=dict)

NUTRITION_RULES = """You are an encouraging, practical nutrition coach for an active adult.
Use common food composition and named brand/restaurant nutrition when verifiable.
Estimate typical servings if quantities are unspecified, disclose assumptions,
and never imply that an estimate is a precise measurement. If an ingredient or
portion is uncertain, make a reasonable assumption and tell the user. Don't
prescribe extreme calorie restriction or diagnose medical conditions.
For energy expenditure, explain that logged workouts, activity, and calorie burn
estimates are uncertain; don't claim access to wearable sensors. Treat goals as
user-set targets, not clinical prescriptions."""

def nutrition_response(prompt: str, instructions: str, search: bool = True):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Add OPENAI_API_KEY to .env and restart the server.")
    client = OpenAI(api_key=api_key)
    model = os.getenv("NUTRITION_MODEL") or os.getenv("OPENAI_MODEL", "gpt-5.5")
    kwargs = dict(model=model, instructions=instructions, input=prompt, max_output_tokens=1400)
    if search:
        kwargs["tools"] = [{"type": "web_search", "search_context_size": "medium"}]
    try:
        response = client.responses.create(**kwargs)
    except Exception as exc:
        if search:
            try:
                kwargs.pop("tools", None)
                response = client.responses.create(**kwargs)
                return response.output_text, False
            except Exception:
                pass
        raise HTTPException(status_code=502, detail=f"Nutrition AI unavailable ({type(exc).__name__}). Check model access and billing.")
    return response.output_text, search

@app.post("/api/nutrition/estimate")
def estimate_nutrition(payload: NutritionRequest, user=Depends(verified_user)):
    instructions = NUTRITION_RULES + """
Return ONLY a valid JSON object with fields name, calories, protein, carbs, fat,
assumptions, sources. Sources is an array of concise source names/URLs, or [] if
no specific source was found. All macro values and calories are numeric >= 0.
If web search is available, research relevant branded or restaurant items.
If no exact item is found, use common food estimates instead. No markdown.
"""
    raw, searched = nutrition_response("Estimate this meal: " + payload.description, instructions)
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise ValueError("Missing JSON")
        data = json.loads(match.group(0))
        result = {"name": str(data.get("name") or payload.description)[:200],
                  "assumptions": str(data.get("assumptions") or "Assumed typical serving sizes.")[:1200],
                  "sources": [str(x)[:220] for x in (data.get("sources") or [])[:5]],
                  "web_search_requested": searched}
        for field in ("calories", "protein", "carbs", "fat"):
            val = float(data[field])
            if not 0 <= val <= 10000:
                raise ValueError("Out-of-range estimate")
            result[field] = round(val, 1)
        return result
    except (ValueError, KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Nutrition estimate could not be parsed. Please retry or enter the macros manually.")

@app.post("/api/nutrition/coach")
def nutrition_coach(payload: NutritionCoachRequest, user=Depends(verified_user)):
    prompt = ("User question: " + payload.message + "\nGoals: " + json.dumps(payload.goals) +
              "\nToday's food totals: " + json.dumps(payload.totals) +
              "\nLogged activity summary: " + json.dumps(payload.activity))
    raw, _ = nutrition_response(prompt, NUTRITION_RULES + "\nReply in conversational plain text, under 220 words.", search=False)
    return {"answer": raw}


# V5 authenticated AI endpoints. The legacy V4 endpoints are retained for compatibility,
# but should be disabled before a public launch (see SECURITY.md).
import httpx
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from cryptography.fernet import Fernet
from datetime import datetime, timezone, timedelta
import secrets

WHOOP_API = "https://api.prod.whoop.com"
WHOOP_DATA = WHOOP_API + "/developer/v2"


class V5Text(BaseModel):
    message: str = Field(min_length=2,max_length=4500)
    history: list[dict[str,str]] = Field(default_factory=list,max_length=16)
    context: dict[str,Any] = Field(default_factory=dict)

async def ai_v5(req:V5Text, kind:str):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(503,"OPENAI_API_KEY missing on Render")
    instructions = ("You are Open Prep, an evidence-informed performance coach. Discuss training, nutrition, "
                    "goal setting, and recovery. Never pretend to access sensors or data not supplied. "
                    "Never diagnose illness or injury. Be specific, concise and practical.")
    if kind=="workout":
        instructions = ("Analyze the athlete's completed workout, not a proposed plan. "
          "Return ONLY valid JSON with keys analysis (string), category (one of CrossFit, Running, Lifting, Biking, Rowing, Ski erg, Walking, Other), "
          "title (string), duration (string), distance_miles (number or null), result (string), "
          "load (string), notes (string). Distinguish unknown facts from estimates. "
          "Do not claim the workout is saved. Ask for user confirmation before logging.")
    msgs=[{"role":x.get("role"),"content":str(x.get("content",""))[:3500]} for x in req.history[-12:] if x.get("role") in ("user","assistant")]
    msgs.append({"role":"user","content":"Context: "+json.dumps(req.context)[:3500]+"\nMessage: "+req.message})
    try:
        result=OpenAI(api_key=os.getenv("OPENAI_API_KEY")).responses.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),instructions=instructions,input=msgs,max_output_tokens=1100)
        if kind=="workout":
            raw=result.output_text.strip();raw=re.sub(r"^```(?:json)?\s*|\s*```$","",raw)
            data=json.loads(raw)
            if not isinstance(data,dict) or not isinstance(data.get("analysis"),str):raise ValueError("Invalid analysis")
            return data
        return {"answer":result.output_text}
    except (ValueError,KeyError,TypeError):
        raise HTTPException(502,"AI could not format the workout analysis. Please retry.")
    except Exception as e:
        raise HTTPException(502,f"AI request failed ({type(e).__name__}). Check model and API access.")

@app.post("/api/v5/chat")
async def v5_chat(req:V5Text, user=Depends(verified_user)):
    return await ai_v5(req,"chat")

@app.post("/api/v5/workout/analyze")
async def v5_workout(req:V5Text,user=Depends(verified_user)):
    return await ai_v5(req,"workout")

def fernet():
    key=os.getenv("WHOOP_TOKEN_ENCRYPTION_KEY","")
    if not key:raise HTTPException(503,"WHOOP_TOKEN_ENCRYPTION_KEY is missing")
    try:return Fernet(key.encode())
    except Exception:raise HTTPException(503,"Invalid WHOOP_TOKEN_ENCRYPTION_KEY")

def admin_config():
    url=os.getenv("SUPABASE_URL","").rstrip("/")
    key=os.getenv("SUPABASE_SERVICE_ROLE_KEY","")
    if not url or not key:raise HTTPException(503,"Configure Supabase server settings for WHOOP")
    return url,key

async def whoop_row(user):
    url,key=admin_config()
    async with httpx.AsyncClient(timeout=15) as h:
        r=await h.get(url+"/rest/v1/open_prep_whoop_tokens",params={"user_id":"eq."+user,"select":"*"},headers={"apikey":key,"Authorization":"Bearer "+key})
    if r.status_code!=200:raise HTTPException(502,"WHOOP token storage unavailable; apply V5 migration SQL")
    return r.json()[0] if r.json() else None

async def store_whoop(user,tokens):
    url,key=admin_config(); cipher=fernet()
    payload={"user_id":user,"token_ciphertext":cipher.encrypt(json.dumps(tokens).encode()).decode(),"updated_at":datetime.now(timezone.utc).isoformat()}
    async with httpx.AsyncClient(timeout=15) as h:
        r=await h.post(url+"/rest/v1/open_prep_whoop_tokens",json=payload,headers={"apikey":key,"Authorization":"Bearer "+key,"Prefer":"resolution=merge-duplicates"})
    if r.status_code not in (200,201,204):raise HTTPException(502,"Could not securely store WHOOP credentials")

@app.get("/api/v5/whoop/start")
async def whoop_start(authorization: str | None=Header(default=None)):
    # Browser redirects cannot carry Authorization headers; initiate from authenticated JS fetch.
    user=await verified_user(authorization)
    client_id=os.getenv("WHOOP_CLIENT_ID")
    redirect=os.getenv("WHOOP_REDIRECT_URI")
    if not client_id or not redirect:raise HTTPException(503,"Configure WHOOP_CLIENT_ID and WHOOP_REDIRECT_URI")
    state=secrets.token_urlsafe(32)
    url,key=admin_config()
    async with httpx.AsyncClient(timeout=15) as h:
        r=await h.post(url+"/rest/v1/open_prep_whoop_states",json={"state":state,"user_id":user},headers={"apikey":key,"Authorization":"Bearer "+key})
    if r.status_code not in (200,201):raise HTTPException(502,"Could not store WHOOP OAuth state. Apply V5 SQL.")
    params={"client_id":client_id,"redirect_uri":redirect,"response_type":"code","scope":"offline read:recovery read:cycles read:sleep read:workout","state":state}
    return {"url":WHOOP_API+"/oauth/oauth2/auth?"+urlencode(params)}

@app.get("/api/v5/whoop/callback")
async def whoop_callback(code:str="",state:str="",error:str=""):
    if error or not code or not state:raise HTTPException(400,"WHOOP authorization cancelled or invalid")
    url,key=admin_config()
    headers={"apikey":key,"Authorization":"Bearer "+key}
    async with httpx.AsyncClient(timeout=20) as h:
        r=await h.get(url+"/rest/v1/open_prep_whoop_states",params={"state":"eq."+state,"select":"*"},headers=headers)
        if r.status_code!=200 or len(r.json())!=1:raise HTTPException(400,"Invalid WHOOP state")
        row=r.json()[0]
        if datetime.fromisoformat(row["created_at"].replace("Z","+00:00")) < datetime.now(timezone.utc)-timedelta(minutes=10):raise HTTPException(400,"Expired WHOOP state")
        # Single-use state: delete before token exchange to prevent replay.
        d=await h.delete(url+"/rest/v1/open_prep_whoop_states",params={"state":"eq."+state},headers=headers)
        if d.status_code not in (200,204):raise HTTPException(502,"Could not consume OAuth state")
        token=await h.post(WHOOP_API+"/oauth/oauth2/token",data={"grant_type":"authorization_code","code":code,"client_id":os.getenv("WHOOP_CLIENT_ID"),"client_secret":os.getenv("WHOOP_CLIENT_SECRET"),"redirect_uri":os.getenv("WHOOP_REDIRECT_URI")})
    if token.status_code!=200:raise HTTPException(502,"WHOOP token exchange failed. Verify developer app redirect and credentials.")
    await store_whoop(row["user_id"],token.json())
    return RedirectResponse(url="/?whoop=connected#v5-recovery",status_code=303)

async def whoop_access(user):
    row=await whoop_row(user)
    if not row:raise HTTPException(404,"WHOOP is not connected")
    tokens=json.loads(fernet().decrypt(row["token_ciphertext"].encode()))
    # Refresh on 401 rather than trusting an unrecorded expiry timestamp.
    return tokens

@app.get("/api/v5/whoop/summary")
async def whoop_summary(user=Depends(verified_user)):
    tokens=await whoop_access(user)
    async with httpx.AsyncClient(timeout=20) as h:
        async def get_all(access):
            heads={"Authorization":"Bearer "+access}
            return [await h.get(WHOOP_DATA+path,params={"limit":1},headers=heads) for path in ("/recovery","/cycle","/activity/sleep","/activity/workout")]
        responses=await get_all(tokens["access_token"])
        if any(r.status_code==401 for r in responses):
            t=await h.post(WHOOP_API+"/oauth/oauth2/token",data={"grant_type":"refresh_token","refresh_token":tokens.get("refresh_token",""),"client_id":os.getenv("WHOOP_CLIENT_ID"),"client_secret":os.getenv("WHOOP_CLIENT_SECRET")})
            if t.status_code!=200:raise HTTPException(401,"WHOOP connection expired; reconnect")
            tokens=t.json();await store_whoop(user,tokens)
            responses=await get_all(tokens["access_token"])
    if any(r.status_code!=200 for r in responses):raise HTTPException(502,"WHOOP API did not return all requested data; check scopes")
    return {k:(r.json().get("records") or [None])[0] for k,r in zip(("recovery","cycle","sleep","workout"),responses)}

@app.delete("/api/v5/whoop/disconnect")
async def whoop_disconnect(user=Depends(verified_user)):
    url,key=admin_config()
    async with httpx.AsyncClient(timeout=15) as h:
        r=await h.delete(url+"/rest/v1/open_prep_whoop_tokens",params={"user_id":"eq."+user},headers={"apikey":key,"Authorization":"Bearer "+key})
    if r.status_code not in (200,204):raise HTTPException(502,"Could not disconnect WHOOP")
    return {"disconnected":True}

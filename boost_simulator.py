#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Growth & Drip-Feed Simulator (100% Organique) pour mysmm.co API v2
----------------------------------------------------------------------------
Orchestre une croissance 100% réaliste et organique pour les Reels Instagram :
1. Triade d'engagement algorithmique : Vues + Likes + Partages (Shares/Reach).
2. Phase d'amorçage réaliste : premiers likes et partages AVANT la 1ère vague de vues,
   suivis d'une période d'observation (rétention algorithmique).
3. Pacing sigmoïde avec micro-variations naturelles (jitter anti-robot).
4. Découpage par cohortes de 100 vues (quantum réel des réseaux SMM Reels)
   avec synchronisation continue des likes (min 10) et des shares (min 10).
5. Visualisation complète (Console ASCII + Image PNG + Dashboard HTML interactif).
6. Mode Simulation par défaut (sans frais) et Mode Live prêt à l'emploi.
"""

import os
import sys
import json
import time
import math
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import requests
except ImportError:
    requests = None

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Configuration par défaut
DEFAULT_API_KEY = os.getenv("MYSMM_API_KEY", "fD5OKMNKEReObZbVooSjlnIuqH7PpKjTunhjMNYIIySTLDOY")
DEFAULT_BASE_URL = os.getenv("MYSMM_BASE_URL", "https://mysmm.co/api/v2")
DEFAULT_LINK = "https://www.instagram.com/reel/DQToIg_k452/"
SERVICES_FILE = "v2.json"

# Services validés sur l'API mysmm.co pour les REELS Instagram :
SERVICE_VIEWS_DEFAULT = "1785"      # Instagram Video/Reel Views (rate: $0.00135/1k, min: 100 réels) - VALIDÉ OK
SERVICE_LIKES_DEFAULT = "1"         # Instagram Likes [Cheapest] [100k/hrs] (rate: $0.0902/1k, min: 10) - VALIDÉ OK
SERVICE_SHARES_DEFAULT = "1581"     # Instagram Shares with Engagement and Reach (rate: $0.1040/1k, min: 10)
SERVICE_COMMENTS_DEFAULT = "1637"   # Instagram Custom Comments [Instant Start] (rate: $0.6292/1k, min: 10) - VALIDÉ OK

DEFAULT_FRENCH_COMMENTS = [
    "Propre ! 🔥", "Masterclass franchement 🙌", "Top niveau 🚀", "Super reel 👏",
    "Valide a 100% 🔥", "Incroyable !", "Trop fort", "J adore 👍",
    "Lourd de fou 🔥", "Bravo pour la video 👏", "Le flow est incroyable 🔥",
    "Du lourd comme d habitude !", "Trop style 🙌", "Carre de fou 👌",
    "Pepite cette video 🚀", "Valide direct 🔥", "Franchement propre 👏",
    "Qualite au max !", "Bien joue 👍", "Totalement merite 🙌"
]


class MySMMClient:
    """Client API v2 pour mysmm.co."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def get_balance(self) -> Dict[str, Any]:
        """Consulte le solde du compte."""
        if not requests:
            raise RuntimeError("Le module 'requests' est requis pour les appels API.")
        params = {"key": self.api_key, "action": "balance"}
        resp = requests.get(self.base_url, params=params, timeout=15)
        return resp.json()

    def add_order(self, service_id: str, link: str, quantity: int, comments: Optional[List[str]] = None, dry_run: bool = True) -> Dict[str, Any]:
        """Passe une commande ou simule l'appel."""
        if dry_run:
            simulated_id = f"SIM_{int(time.time()*1000) % 100000000}"
            return {"order": simulated_id, "simulated": True}

        if not requests:
            raise RuntimeError("Le module 'requests' est requis pour les appels API.")
        data = {
            "key": self.api_key,
            "action": "add",
            "service": str(service_id),
            "link": link,
            "quantity": int(quantity)
        }
        if comments:
            data["comments"] = "\r\n".join(comments)
        resp = requests.post(self.base_url, data=data, timeout=20)
        try:
            return resp.json()
        except Exception:
            return {"error": resp.text, "status_code": resp.status_code}

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Vérifie le statut d'un ordre."""
        if not requests:
            raise RuntimeError("Le module 'requests' est requis pour les appels API.")
        data = {
            "key": self.api_key,
            "action": "status",
            "order": str(order_id)
        }
        resp = requests.post(self.base_url, data=data, timeout=15)
        return resp.json()


class CatalogManager:
    """Gestionnaire des tarifs et métadonnées des services à partir de v2.json."""

    def __init__(self, json_path: str = SERVICES_FILE):
        self.services: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                    for item in raw:
                        self.services[str(item.get("service"))] = item
            except Exception as e:
                print(f"[!] Avertissement : impossible de charger {json_path}: {e}")

    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        return self.services.get(str(service_id))

    def calculate_cost(self, service_id: str, quantity: int) -> float:
        srv = self.get_service(service_id)
        if not srv:
            return 0.0
        try:
            rate = float(srv.get("rate", 0.0))
            return (quantity / 1000.0) * rate
        except (ValueError, TypeError):
            return 0.0


def estimate_duration_hours(views: int) -> float:
    """
    Estime une durée réaliste en heures pour qu'un Reel prenne de l'ampleur
    de manière naturelle sur Instagram.
    """
    if views <= 500:
        return 4.0
    elif views <= 1000:
        return 6.0
    elif views <= 2000:
        return 8.0
    elif views <= 5000:
        return 14.0
    elif views <= 10000:
        return 24.0
    else:
        return round(24.0 + (views - 10000) / 5000.0 * 6.0, 1)


def sigmoid_time_mapping(fraction: float, total_minutes: float) -> float:
    """
    Mappe une fraction de progression [0..1] vers un instant T selon la courbe
    de diffusion d'un Reel Instagram (départ doux, pic médian, plateau).
    """
    fraction = max(0.0001, min(0.9999, fraction))
    k = 5.0
    p0 = 0.42  # pic de pente autour de 40-45% du temps total
    s_min = 1.0 / (1.0 + math.exp(-k * (0.0 - p0)))
    s_max = 1.0 / (1.0 + math.exp(-k * (1.0 - p0)))

    s = fraction * (s_max - s_min) + s_min
    p = p0 - math.log(1.0 / s - 1.0) / k
    p = max(0.0, min(1.0, p))
    return p * total_minutes


def apply_jitter(minutes: float, jitter_pct: float = 0.12) -> float:
    """Ajoute une micro-variation pseudo-aléatoire pour casser toute régularité robotique."""
    delta = (random.random() * 2 - 1) * (minutes * jitter_pct)
    return max(0.5, minutes + delta)


def build_organic_plan(
    target_views: int = 2000,
    duration_hours: float = 8.0,
    like_ratio: float = 0.05,
    share_ratio: float = 0.015,
    include_shares: bool = False,
    include_comments: bool = False,
    comments_count: Optional[int] = None,
    catalog: Optional[CatalogManager] = None,
    service_views: str = SERVICE_VIEWS_DEFAULT,
    service_likes: str = SERVICE_LIKES_DEFAULT,
    service_shares: str = SERVICE_SHARES_DEFAULT,
    service_comments: str = SERVICE_COMMENTS_DEFAULT,
    custom_comments_pool: Optional[List[str]] = None,
    link: str = DEFAULT_LINK,
    use_jitter: bool = True
) -> Dict[str, Any]:
    """
    Construit une simulation 100% organique basée sur les Vues et les Likes
    (optionnellement les Partages avec --with-shares et Commentaires avec --with-comments).
    """
    if catalog is None:
        catalog = CatalogManager()

    total_minutes = duration_hours * 60.0

    # 1. Découpage des vues par tranches de 100 (quantum réel de livraison des Reels)
    batches_count = max(1, int(math.ceil(target_views / 100.0)))
    real_target_views = batches_count * 100

    # 2. Cibles d'engagement associées (min 10 par commande)
    target_likes = max(10, int(round((real_target_views * like_ratio) / 10.0) * 10))
    target_shares = max(10, int(round((real_target_views * share_ratio) / 10.0) * 10)) if include_shares else 0

    if include_comments:
        if comments_count is not None and comments_count > 0:
            target_comments = max(10, int(round(comments_count / 10.0) * 10))
        else:
            # Règle algorithmique réaliste : 10 coms si < 5000 vues, 20 coms si >= 5000 vues
            target_comments = max(10, min(40, int(math.ceil(real_target_views / 5000.0) * 10)))
    else:
        target_comments = 0

    events = []

    # =========================================================================
    # PHASE 1 : AMORÇAGE INITIAL (T = 0 à 15% de la durée)
    # Sur un vrai post, les premiers abonnés likent d'abord !
    # =========================================================================
    # T = 2 min : 1er lot de 10 likes
    t_first_like = 2.0
    events.append({
        "type": "LIKES",
        "time_minutes": t_first_like,
        "quantity": 10,
        "service": service_likes,
        "phase": "Amorçage (Signaux précoces)",
        "link": link
    })

    if include_shares:
        # T = 5 min : 1er lot de 10 shares si activé
        events.append({
            "type": "SHARES",
            "time_minutes": 5.0,
            "quantity": 10,
            "service": service_shares,
            "phase": "Amorçage (Viralité initiale)",
            "link": link
        })

    # T = 8 min : 1ère vague de 100 vues
    t_first_view = 8.0
    events.append({
        "type": "VIEWS",
        "time_minutes": t_first_view,
        "quantity": 100,
        "service": service_views,
        "phase": "Amorçage (1ère cohorte de vues)",
        "link": link
    })

    # =========================================================================
    # PHASE 2 & 3 : CROISSANCE SIGMOÏDE & PLATÉAU (Vues restantes)
    # =========================================================================
    remaining_view_batches = batches_count - 1
    if remaining_view_batches > 0:
        for idx in range(1, batches_count):
            frac = (idx + 1) / float(batches_count)
            t_base = sigmoid_time_mapping(frac, total_minutes)
            t_view = max(t_first_view + 25.0, t_base)  # Grande pause d'observation initiale
            if use_jitter:
                t_view = apply_jitter(t_view, 0.04)

            phase_name = "Accélération virale (Reels Tab)" if frac < 0.70 else "Plateau (Stabilisation)"
            events.append({
                "type": "VIEWS",
                "time_minutes": min(total_minutes - 1.0, t_view),
                "quantity": 100,
                "service": service_views,
                "phase": phase_name,
                "link": link
            })

    # =========================================================================
    # LIKES RESTANTS (Cadencés selon la montée des vues)
    # =========================================================================
    remaining_likes_batches = (target_likes // 10) - 1
    if remaining_likes_batches > 0:
        for l_idx in range(1, target_likes // 10):
            frac = (l_idx + 1) / float(target_likes // 10)
            t_base = sigmoid_time_mapping(frac, total_minutes)
            # Petit décalage pour ne pas superposer pile avec les vues
            t_like = max(18.0, t_base + 3.5)
            if use_jitter:
                t_like = apply_jitter(t_like, 0.05)

            events.append({
                "type": "LIKES",
                "time_minutes": min(total_minutes - 2.0, t_like),
                "quantity": 10,
                "service": service_likes,
                "phase": "Engagement proportionnel",
                "link": link
            })

    # =========================================================================
    # SHARES RESTANTS (Cadencés aux points culminants)
    # =========================================================================
    remaining_shares_batches = (target_shares // 10) - 1
    if remaining_shares_batches > 0:
        for s_idx in range(1, target_shares // 10):
            frac = (s_idx + 1) / float(target_shares // 10)
            t_base = sigmoid_time_mapping(frac, total_minutes)
            t_share = max(22.0, t_base + 7.0)
            if use_jitter:
                t_share = apply_jitter(t_share, 0.05)

            events.append({
                "type": "SHARES",
                "time_minutes": min(total_minutes - 3.0, t_share),
                "quantity": 10,
                "service": service_shares,
                "phase": "Amplification de portée",
                "link": link
            })

    # =========================================================================
    # COMMENTAIRES NATURELS (Phase d'accélération virale UNIQUEMENT)
    # Règle algorithmique : Jamais au tout début quand la vidéo a peu de vues !
    # =========================================================================
    if target_comments > 0:
        comment_batches = target_comments // 10
        pool = list(custom_comments_pool or DEFAULT_FRENCH_COMMENTS)
        random.shuffle(pool)

        for c_idx in range(comment_batches):
            if comment_batches == 1:
                # 1 seul lot de 10 : injecté à ~38% de la durée (pleine accélération)
                frac = 0.38
            else:
                # Plusieurs lots : étalés entre 35% et 75% de la durée
                frac = 0.35 + (c_idx / float(comment_batches)) * 0.40

            t_base = sigmoid_time_mapping(frac, total_minutes)
            t_comment = max(25.0, t_base + 4.5)
            if use_jitter:
                t_comment = apply_jitter(t_comment, 0.04)

            # Sélectionner 10 commentaires variés du pool
            batch_comments = []
            for k in range(10):
                batch_comments.append(pool[(c_idx * 10 + k) % len(pool)])

            phase_name = "Engagement conversationnel (Preuve sociale)" if c_idx == 0 else "Relance de viralité & discussion"
            events.append({
                "type": "COMMENTS",
                "time_minutes": min(total_minutes - 4.0, t_comment),
                "quantity": 10,
                "service": service_comments,
                "comments": batch_comments,
                "phase": phase_name,
                "link": link
            })

    # Tri chronologique strict
    events.sort(key=lambda x: x["time_minutes"])

    # Construction de la chronologie avec cumuls et pauses
    cum_views = 0
    cum_likes = 0
    cum_shares = 0
    cum_comments = 0
    total_cost = 0.0
    timeline = []

    for i, ev in enumerate(events):
        qty = ev["quantity"]
        cost = catalog.calculate_cost(ev["service"], qty)
        total_cost += cost

        if ev["type"] == "VIEWS":
            cum_views += qty
        elif ev["type"] == "LIKES":
            cum_likes += qty
        elif ev["type"] == "SHARES":
            cum_shares += qty
        elif ev["type"] == "COMMENTS":
            cum_comments += qty

        if i < len(events) - 1:
            pause_min = max(0.5, events[i + 1]["time_minutes"] - ev["time_minutes"])
        else:
            pause_min = 0.0

        srv_meta = catalog.get_service(ev["service"]) or {}
        srv_name = srv_meta.get("name", "Service inconnu")

        timeline.append({
            "step": i + 1,
            "type": ev["type"],
            "minute": round(ev["time_minutes"], 1),
            "time_str": format_minutes(ev["time_minutes"]),
            "quantity": qty,
            "service_id": ev["service"],
            "service_name": srv_name,
            "comments": ev.get("comments"),
            "phase": ev["phase"],
            "cost": round(cost, 6),
            "pause_min": round(pause_min, 1),
            "pause_seconds": int(round(pause_min * 60)),
            "cum_views": cum_views,
            "cum_likes": cum_likes,
            "cum_shares": cum_shares,
            "cum_comments": cum_comments,
            "link": ev["link"]
        })

    return {
        "target_views": real_target_views,
        "target_likes": target_likes,
        "target_shares": target_shares,
        "target_comments": target_comments,
        "like_ratio_pct": round((target_likes / real_target_views) * 100, 1),
        "share_ratio_pct": round((target_shares / real_target_views) * 100, 2),
        "duration_hours": duration_hours,
        "total_minutes": total_minutes,
        "total_cost_usd": round(total_cost, 6),
        "total_orders": len(timeline),
        "breakdown": {
            "views_batches": batches_count,
            "views_service": service_views,
            "likes_batches": target_likes // 10,
            "likes_service": service_likes,
            "shares_batches": target_shares // 10,
            "shares_service": service_shares,
            "comments_batches": target_comments // 10,
            "comments_service": service_comments
        },
        "timeline": timeline
    }


def format_minutes(minutes: float) -> str:
    """Convertit des minutes en chaîne 'T+HH:MM'."""
    hrs = int(minutes // 60)
    mins = int(minutes % 60)
    return f"T+{hrs:02d}h{mins:02d}"


# =====================================================================
# VISUALISATION : CONSOLE ASCII
# =====================================================================

def render_ascii_chart(plan: Dict[str, Any], width: int = 65, height: int = 14) -> str:
    """Génère un graphique ASCII de la courbe de croissance en console."""
    timeline = plan["timeline"]
    total_minutes = plan["total_minutes"]
    target_views = plan["target_views"]

    grid = [[" " for _ in range(width)] for _ in range(height)]

    for col in range(width):
        curr_min = (col / (width - 1)) * total_minutes
        views_at_t = 0
        for ev in timeline:
            if ev["minute"] <= curr_min:
                views_at_t = ev["cum_views"]
            else:
                break
        y_ratio = views_at_t / float(target_views) if target_views > 0 else 0
        row = height - 1 - int(y_ratio * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = "#"
        for r in range(row + 1, height):
            if grid[r][col] == " ":
                grid[r][col] = "."

    lines = []
    lines.append("   Vues")
    for r in range(height):
        label_val = int(target_views * (1.0 - (r / (height - 1))))
        y_label = f"{label_val:>6} |"
        row_str = "".join(grid[r])
        lines.append(f"{y_label}{row_str}")

    lines.append("        +" + "-" * width)
    t_start = "T+00h"
    t_mid = f"T+{int(plan['duration_hours']/2):02d}h"
    t_end = f"T+{int(plan['duration_hours']):02d}h"
    spacing1 = (width // 2) - len(t_start) - 1
    spacing2 = width - (width // 2) - len(t_end) - len(t_mid) + 1
    lines.append(f"         {t_start}{' ' * max(1, spacing1)}{t_mid}{' ' * max(1, spacing2)}{t_end}")
    lines.append(f"         {'Temps ecoule (duree totale : ' + str(plan['duration_hours']) + 'h)'}")

    return "\n".join(lines)


# =====================================================================
# VISUALISATION : RAPPORT GRAPHIQUE PNG (TRIPLE COURBE)
# =====================================================================

def export_plot_png(plan: Dict[str, Any], output_path: str = "simulation_curve.png") -> bool:
    """Génère un graphique élégant avec les 3 signaux : Vues, Likes et Shares."""
    if not HAS_MATPLOTLIB:
        return False

    timeline = plan["timeline"]
    times = [0.0] + [e["minute"] / 60.0 for e in timeline]
    views = [0] + [e["cum_views"] for e in timeline]
    likes = [0] + [e["cum_likes"] for e in timeline]
    shares = [0] + [e["cum_shares"] for e in timeline]
    comments = [0] + [e.get("cum_comments", 0) for e in timeline]

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
    fig.patch.set_facecolor('#0f172a')
    ax1.set_facecolor('#1e293b')

    color_views = '#38bdf8'
    ax1.set_xlabel('Temps écoulé (Heures)', color='#cbd5e1', fontsize=11, labelpad=10)
    ax1.set_ylabel('Vues cumulées', color=color_views, fontsize=11, labelpad=10)
    line1 = ax1.plot(times, views, color=color_views, linewidth=2.6, label='Vues (Reels Tab)', marker='o', markersize=3)
    ax1.fill_between(times, views, color=color_views, alpha=0.12)
    ax1.tick_params(axis='x', colors='#94a3b8')
    ax1.tick_params(axis='y', colors=color_views)
    ax1.grid(True, linestyle='--', alpha=0.18, color='#64748b')

    # Axe secondaire pour les interactions
    ax2 = ax1.twinx()
    color_likes = '#f43f5e'
    color_shares = '#a855f7'
    color_comments = '#10b981'
    ax2.set_ylabel('Interactions cumulées (Likes / Shares / Coms)', color='#e2e8f0', fontsize=11, labelpad=10)
    line2 = ax2.plot(times, likes, color=color_likes, linewidth=2.0, linestyle='--', label=f'Likes ({plan["like_ratio_pct"]}%)', marker='s', markersize=3)
    lines_all = line1 + line2

    if plan.get("target_shares", 0) > 0:
        line3 = ax2.plot(times, shares, color=color_shares, linewidth=2.0, linestyle=':', label=f'Partages ({plan["share_ratio_pct"]}%)', marker='^', markersize=3)
        lines_all += line3

    if plan.get("target_comments", 0) > 0:
        line4 = ax2.plot(times, comments, color=color_comments, linewidth=2.0, linestyle='-.', label=f'Commentaires ({plan["target_comments"]})', marker='d', markersize=3)
        lines_all += line4

    ax2.tick_params(axis='y', colors='#e2e8f0')

    title = f"Simulation 100% Organique Instagram : {plan['target_views']:,} Vues ({plan['duration_hours']}h)"
    plt.title(title, color='#f8fafc', fontsize=12.5, weight='bold', pad=15)

    labels = [l.get_label() for l in lines_all]
    legend = ax1.legend(lines_all, labels, loc='upper left', facecolor='#0f172a', edgecolor='#334155')
    for text in legend.get_texts():
        text.set_color('#e2e8f0')

    summary_txt = (
        f"Durée : {plan['duration_hours']}h\n"
        f"Ordres totaux : {plan['total_orders']}\n"
        f"Vues : {plan['target_views']:,}\n"
        f"Likes : {plan['target_likes']}\n"
        f"Partages : {plan['target_shares']}\n"
        f"Commentaires : {plan.get('target_comments', 0)}\n"
        f"Coût total : ${plan['total_cost_usd']:.4f} USD"
    )
    ax1.text(0.70, 0.10, summary_txt, transform=ax1.transAxes, fontsize=9.0,
             color='#f1f5f9', verticalalignment='bottom',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#0f172a', edgecolor='#475569', alpha=0.92))

    plt.tight_layout()
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    return True


# =====================================================================
# VISUALISATION : RAPPORT HTML COMPLET AVEC CHART.JS
# =====================================================================

def export_html_report(plan: Dict[str, Any], output_path: str = "simulation_report.html") -> str:
    """Génère un tableau de bord HTML complet et interactif."""
    timeline = plan["timeline"]
    labels_chart = [e["time_str"] for e in timeline]
    data_views = [e["cum_views"] for e in timeline]
    data_likes = [e["cum_likes"] for e in timeline]
    data_shares = [e["cum_shares"] for e in timeline]
    data_comments = [e.get("cum_comments", 0) for e in timeline]

    table_rows = []
    for e in timeline:
        if e["type"] == "VIEWS":
            badge_cls = "badge-views"
            badge_text = f"+{e['quantity']} Vues"
        elif e["type"] == "LIKES":
            badge_cls = "badge-likes"
            badge_text = f"+{e['quantity']} Likes"
        elif e["type"] == "SHARES":
            badge_cls = "badge-shares"
            badge_text = f"+{e['quantity']} Partages"
        elif e["type"] == "COMMENTS":
            badge_cls = "badge-comments"
            badge_text = f"+{e['quantity']} Coms"
        else:
            badge_cls = "badge-shares"
            badge_text = f"+{e['quantity']} {e['type']}"

        pause_str = f"{e['pause_min']} min ({e['pause_seconds']}s)" if e['pause_seconds'] > 0 else "Objectif atteint"

        row = f"""
        <tr>
            <td class="font-mono text-xs">{e['step']}</td>
            <td class="font-mono font-bold text-sky-400">{e['time_str']}</td>
            <td><span class="{badge_cls}">{badge_text}</span></td>
            <td class="text-xs text-slate-300">#{e['service_id']} - {e['service_name']}</td>
            <td class="text-xs italic text-slate-400">{e['phase']}</td>
            <td class="font-mono text-emerald-400 text-xs">${e['cost']:.6f}</td>
            <td class="font-mono text-amber-300 text-xs">{pause_str}</td>
            <td class="font-mono font-semibold text-slate-100">{e['cum_views']}</td>
            <td class="font-mono font-semibold text-rose-400">{e['cum_likes']}</td>
            <td class="font-mono font-semibold text-purple-400">{e['cum_shares']}</td>
            <td class="font-mono font-semibold text-emerald-400">{e.get('cum_comments', 0)}</td>
        </tr>
        """
        table_rows.append(row)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Simulation 100% Organique Instagram - {plan['target_views']} Vues</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #0b1120; color: #f8fafc; font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; }}
        .badge-views {{ background-color: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
        .badge-likes {{ background-color: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
        .badge-shares {{ background-color: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
        .badge-comments {{ background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
        tr:hover {{ background-color: rgba(30, 41, 59, 0.7); }}
    </style>
</head>
<body class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-8 border-b border-slate-800 pb-6 flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
            <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-indigo-400 to-rose-400">
                Simulation 100% Organique (Instagram Reels)
            </h1>
            <p class="text-slate-400 mt-1">Quadriptyque algorithmique : Vues + Likes + Partages + Commentaires avec pacing sigmoïde</p>
        </div>
        <div class="mt-4 md:mt-0 flex items-center space-x-3">
            <span class="bg-indigo-900 text-indigo-300 text-xs px-3 py-1 rounded-full font-mono">mysmm.co v2</span>
            <span class="bg-emerald-900 text-emerald-300 text-xs px-3 py-1 rounded-full font-mono">Anti-Détection Actif</span>
        </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400 uppercase tracking-wider">Objectif Vues</div>
            <div class="text-2xl font-black text-sky-400 mt-1">{plan['target_views']:,}</div>
            <div class="text-xs text-slate-500 mt-1">{plan['breakdown']['views_batches']} x 100 vues (#1785)</div>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400 uppercase tracking-wider">Likes Associés</div>
            <div class="text-2xl font-black text-rose-500 mt-1">{plan['target_likes']}</div>
            <div class="text-xs text-slate-500 mt-1">{plan['like_ratio_pct']}% ratio ({plan['breakdown']['likes_batches']} x 10)</div>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400 uppercase tracking-wider">Partages (Shares)</div>
            <div class="text-2xl font-black text-purple-400 mt-1">{plan['target_shares']}</div>
            <div class="text-xs text-slate-500 mt-1">{plan['share_ratio_pct']}% ratio ({plan['breakdown']['shares_batches']} x 10)</div>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400 uppercase tracking-wider">Commentaires</div>
            <div class="text-2xl font-black text-emerald-400 mt-1">{plan.get('target_comments', 0)}</div>
            <div class="text-xs text-slate-500 mt-1">{plan['breakdown']['comments_batches']} x 10 coms (#1637)</div>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400 uppercase tracking-wider">Durée & Ordres</div>
            <div class="text-2xl font-black text-amber-400 mt-1">{plan['duration_hours']} h</div>
            <div class="text-xs text-slate-500 mt-1">{plan['total_orders']} étapes échelonnées</div>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div class="text-xs text-slate-400 uppercase tracking-wider">Coût Total Réel</div>
            <div class="text-2xl font-black text-emerald-400 mt-1">${plan['total_cost_usd']:.4f}</div>
            <div class="text-xs text-slate-500 mt-1">USD (Tout inclus)</div>
        </div>
    </div>

    <!-- Graphique interactif -->
    <div class="bg-slate-900 p-6 rounded-xl border border-slate-800 mb-8">
        <h2 class="text-lg font-bold text-slate-200 mb-4 flex items-center">
            Courbe de Croissance Multi-Signaux (Chart.js)
        </h2>
        <div style="height: 380px;">
            <canvas id="growthChart"></canvas>
        </div>
    </div>

    <!-- Tableau chronologique -->
    <div class="bg-slate-900 p-6 rounded-xl border border-slate-800">
        <h2 class="text-lg font-bold text-slate-200 mb-4 flex items-center">
            Déroulé Chronologique Détaillé
        </h2>
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead>
                    <tr class="border-b border-slate-800 text-slate-400 uppercase text-xs">
                        <th class="py-3 px-2">#</th>
                        <th class="py-3 px-2">Temps</th>
                        <th class="py-3 px-2">Action</th>
                        <th class="py-3 px-2">Service</th>
                        <th class="py-3 px-2">Rôle algorithmique</th>
                        <th class="py-3 px-2">Coût</th>
                        <th class="py-3 px-2">Pause suivante</th>
                        <th class="py-3 px-2">Cumul Vues</th>
                        <th class="py-3 px-2">Cumul Likes</th>
                        <th class="py-3 px-2">Cumul Shares</th>
                        <th class="py-3 px-2">Cumul Coms</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800">
                    {"".join(table_rows)}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('growthChart').getContext('2d');
        const labels = {json.dumps(labels_chart)};
        const viewsData = {json.dumps(data_views)};
        const likesData = {json.dumps(data_likes)};
        const sharesData = {json.dumps(data_shares)};
        const commentsData = {json.dumps(data_comments)};

        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: 'Vues cumulées',
                        data: viewsData,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.08)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.35,
                        yAxisID: 'y'
                    }},
                    {{
                        label: 'Likes cumulés',
                        data: likesData,
                        borderColor: '#f43f5e',
                        borderWidth: 2,
                        borderDash: [5, 4],
                        fill: false,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }},
                    {{
                        label: 'Partages cumulés',
                        data: sharesData,
                        borderColor: '#c084fc',
                        borderWidth: 2,
                        borderDash: [2, 3],
                        fill: false,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }},
                    {{
                        label: 'Commentaires cumulés',
                        data: commentsData,
                        borderColor: '#34d399',
                        borderWidth: 2,
                        borderDash: [3, 3],
                        fill: false,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode: 'index', intersect: false }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255, 255, 255, 0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#38bdf8' }},
                        title: {{ display: true, text: 'Vues', color: '#38bdf8' }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {{ drawOnChartArea: false }},
                        ticks: {{ color: '#f43f5e' }},
                        title: {{ display: true, text: 'Likes & Partages', color: '#f43f5e' }}
                    }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#cbd5e1' }} }} }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path


# =====================================================================
# EXÉCUTION RÉELLE (MODE LIVE)
# =====================================================================

def execute_live_run(plan: Dict[str, Any], api_client: MySMMClient, auto_confirm: bool = False):
    """Exécute le plan en réel avec pauses effectives et appels API mysmm.co."""
    print("\n" + "=" * 65)
    print("ATTENTION : EXECUTION EN DIRECT SUR MYSMM.CO")
    print("=" * 65)
    print(f"Lien cible        : {plan['timeline'][0]['link'] if plan['timeline'] else 'N/A'}")
    print(f"Total ordres      : {plan['total_orders']}")
    print(f"Vues prévues      : {plan['target_views']:,}")
    print(f"Likes prévus      : {plan['target_likes']}")
    print(f"Partages prévus   : {plan['target_shares']}")
    print(f"Commentaires      : {plan.get('target_comments', 0)}")
    print(f"Coût total prévu  : ${plan['total_cost_usd']:.4f} USD")
    print(f"Durée totale      : {plan['duration_hours']}h")
    print("=" * 65)

    try:
        bal = api_client.get_balance()
        print(f"[i] Solde actuel sur mysmm.co : {bal.get('balance', 'Inconnu')} {bal.get('currency', 'USD')}")
    except Exception as e:
        print(f"[!] Erreur de verification du solde : {e}")

    if not auto_confirm:
        try:
            confirm = input("\nConfirmez-vous le lancement reel ? (tapez 'OUI' pour valider) : ").strip()
        except (EOFError, Exception):
            confirm = "NON"
        if confirm != "OUI":
            print("[-] Operation annulee par l'utilisateur.")
            return
    else:
        print("[i] Confirmation automatique activee (--yes).")

    print("\n[+] Demarrage du drip-feed en direct...")
    timeline = plan["timeline"]
    for i, step in enumerate(timeline):
        print(f"\n[{step['time_str']}] Etape {step['step']}/{len(timeline)} : "
              f"+{step['quantity']} {step['type']} (Service #{step['service_id']}) -> {step['phase']}")

        try:
            res = api_client.add_order(
                service_id=step["service_id"],
                link=step["link"],
                quantity=step["quantity"],
                comments=step.get("comments"),
                dry_run=False
            )
            if "order" in res:
                print(f"  [OK] Ordre valide avec succes ! ID = {res['order']}")
            else:
                print(f"  [FAIL] Erreur de l'API : {res}")
        except Exception as err:
            print(f"  [FAIL] Exception reseau/API : {err}")

        # Pause si nécessaire
        if step["pause_seconds"] > 0:
            pause_sec = step["pause_seconds"]
            print(f"  [..] Pause de {step['pause_min']} min ({pause_sec}s)... (Appuyez sur Ctrl+C pour interrompre)")
            try:
                step_sleep = min(5, pause_sec)
                elapsed = 0
                while elapsed < pause_sec:
                    time.sleep(step_sleep)
                    elapsed += step_sleep
                    remaining = pause_sec - elapsed
                    sys.stdout.write(f"\r     Reste : {remaining // 60}m {remaining % 60}s  ")
                    sys.stdout.flush()
                print()
            except KeyboardInterrupt:
                print("\n[!] Pause interrompue par l'utilisateur.")
                stop = input("Voulez-vous stopper l'execution ? (o/n) : ").lower().strip()
                if stop == 'o':
                    print("Arret de l'execution.")
                    break

    print("\n[+] Plan d'execution termine avec succes !")


# =====================================================================
# POINT D'ENTRÉE ET CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Simulateur de croissance 100% organique Instagram pour mysmm.co v2"
    )
    parser.add_argument("--views", "-v", type=int, default=None,
                        help="Nombre total de vues cibles (ex: 2000)")
    parser.add_argument("--hours", "-t", type=float, default=None,
                        help="Durée totale souhaitée en heures (optionnel, calculée auto sinon)")
    parser.add_argument("--likes-ratio", "-l", type=float, default=0.05,
                        help="Ratio de likes par rapport aux vues (défaut: 0.05 = 5%%)")
    parser.add_argument("--shares-ratio", "-s", type=float, default=0.015,
                        help="Ratio de partages par rapport aux vues (défaut: 0.015 = 1.5%%)")
    parser.add_argument("--with-shares", action="store_true",
                        help="Active l'envoi de partages (désactivé par défaut)")
    parser.add_argument("--with-comments", action="store_true",
                        help="Active l'envoi de commentaires naturels en français (décalés lors de l'accélération virale)")
    parser.add_argument("--comments-count", type=int, default=None,
                        help="Nombre total de commentaires cibles (par tranches de 10, ex: 10, 20)")
    parser.add_argument("--test-likes", type=str, default=None,
                        help="Envoie immédiatement 10 likes sur le lien spécifié pour tester")
    parser.add_argument("--test-views", type=str, default=None,
                        help="Envoie immédiatement 100 vues sur le lien spécifié pour tester")
    parser.add_argument("--test-shares", type=str, default=None,
                        help="Envoie immédiatement 10 partages sur le lien spécifié pour tester")
    parser.add_argument("--test-comments", type=str, default=None,
                        help="Envoie immédiatement 10 commentaires de test en français sur le lien spécifié")
    parser.add_argument("--link", type=str, default=DEFAULT_LINK,
                        help=f"Lien du Reel (défaut: {DEFAULT_LINK})")
    parser.add_argument("--key", type=str, default=DEFAULT_API_KEY,
                        help="Clé API mysmm.co")
    parser.add_argument("--live", action="store_true",
                        help="Exécute les commandes réelles sur l'API (nécessite confirmation)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Valide automatiquement sans demander confirmation en mode --live")
    parser.add_argument("--balance", action="store_true",
                        help="Affiche le solde actuel sur mysmm.co et quitte")
    parser.add_argument("--status", type=str, default=None,
                        help="Vérifie le statut d'un order_id sur mysmm.co et quitte")
    parser.add_argument("--service-views", type=str, default=SERVICE_VIEWS_DEFAULT,
                        help=f"Service ID pour vues Reels (défaut: {SERVICE_VIEWS_DEFAULT})")
    parser.add_argument("--service-likes", type=str, default=SERVICE_LIKES_DEFAULT,
                        help=f"Service ID pour likes (défaut: {SERVICE_LIKES_DEFAULT})")
    parser.add_argument("--service-shares", type=str, default=SERVICE_SHARES_DEFAULT,
                        help=f"Service ID pour shares (défaut: {SERVICE_SHARES_DEFAULT})")
    parser.add_argument("--service-comments", type=str, default=SERVICE_COMMENTS_DEFAULT,
                        help=f"Service ID pour commentaires (défaut: {SERVICE_COMMENTS_DEFAULT})")

    args = parser.parse_args()

    api_client = MySMMClient(api_key=args.key)

    if args.balance:
        print("Vérification du solde sur mysmm.co...")
        try:
            bal = api_client.get_balance()
            print(f"Solde : {bal.get('balance')} {bal.get('currency', 'USD')}")
        except Exception as e:
            print(f"Erreur : {e}")
        return

    if args.status:
        print(f"Vérification du statut de la commande #{args.status}...")
        try:
            st = api_client.get_order_status(args.status)
            print(f"Statut : {json.dumps(st, indent=2)}")
        except Exception as e:
            print(f"Erreur : {e}")
        return

    if args.test_likes:
        print(f"Envoi de 10 likes de test (Service #{args.service_likes}) sur : {args.test_likes}")
        res = api_client.add_order(args.service_likes, args.test_likes, 10, dry_run=False)
        print("Reponse API :", res)
        return

    if args.test_views:
        print(f"Envoi de 100 vues de test (Service #{args.service_views}) sur : {args.test_views}")
        res = api_client.add_order(args.service_views, args.test_views, 100, dry_run=False)
        print("Reponse API :", res)
        return

    if args.test_shares:
        print(f"Envoi de 10 partages de test (Service #{args.service_shares}) sur : {args.test_shares}")
        res = api_client.add_order(args.service_shares, args.test_shares, 10, dry_run=False)
        print("Reponse API :", res)
        return

    if args.test_comments:
        print(f"Envoi de 10 commentaires de test (Service #{args.service_comments}) sur : {args.test_comments}")
        test_comms = DEFAULT_FRENCH_COMMENTS[:10]
        res = api_client.add_order(args.service_comments, args.test_comments, 10, comments=test_comms, dry_run=False)
        print("Reponse API :", res)
        return

    target_views = args.views
    if target_views is None:
        if sys.stdin.isatty():
            print("\n" + "=" * 60)
            print("  SIMULATEUR DE CROISSANCE 100% ORGANIQUE INSTAGRAM REELS")
            print("=" * 60)
            try:
                val = input("Nombre de vues souhaité [ex: 2000] : ").strip()
                target_views = int(val) if val else 2000
            except (EOFError, Exception):
                target_views = 2000
        else:
            target_views = 2000

    estimated_hours = estimate_duration_hours(target_views)
    duration_hours = args.hours
    if duration_hours is None:
        if sys.stdin.isatty():
            print(f"\nDurée organique recommandée pour {target_views:,} vues : {estimated_hours}h")
            try:
                user_h = input(f"Entrez la durée en heures souhaitée [Entrée pour garder {estimated_hours}h] : ").strip()
                if user_h:
                    duration_hours = float(user_h)
                else:
                    duration_hours = estimated_hours
            except (ValueError, EOFError, Exception):
                duration_hours = estimated_hours
        else:
            duration_hours = estimated_hours

    catalog = CatalogManager(SERVICES_FILE)

    plan = build_organic_plan(
        target_views=target_views,
        duration_hours=duration_hours,
        like_ratio=args.likes_ratio,
        share_ratio=args.shares_ratio,
        include_shares=args.with_shares,
        include_comments=args.with_comments,
        comments_count=args.comments_count,
        catalog=catalog,
        service_views=args.service_views,
        service_likes=args.service_likes,
        service_shares=args.service_shares,
        service_comments=args.service_comments,
        link=args.link,
        use_jitter=True
    )

    json_path = "simulation_plan.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    ascii_chart = render_ascii_chart(plan)

    png_path = "simulation_curve.png"
    export_plot_png(plan, png_path)

    html_path = "simulation_report.html"
    export_html_report(plan, html_path)

    # Affichage récapitulatif
    print("\n" + "=" * 65)
    print(f"   PLAN DE CROISSANCE 100% ORGANIQUE : {plan['target_views']:,} VUES ({plan['duration_hours']}h)")
    print("=" * 65)
    print(f"* Vues Reels (Reels Tab)  : {plan['target_views']:,} vues ({plan['breakdown']['views_batches']} x 100) -> #{args.service_views}")
    print(f"* Likes naturels           : {plan['target_likes']} likes ({plan['like_ratio_pct']}% ratio) ({plan['breakdown']['likes_batches']} x 10) -> #{args.service_likes}")
    if plan['target_shares'] > 0:
        print(f"* Partages & Engagement    : {plan['target_shares']} partages ({plan['share_ratio_pct']}% ratio) ({plan['breakdown']['shares_batches']} x 10) -> #{args.service_shares}")
    if plan.get('target_comments', 0) > 0:
        print(f"* Commentaires naturels    : {plan['target_comments']} commentaires ({plan['breakdown']['comments_batches']} x 10) -> #{args.service_comments}")
    print(f"* Durée totale             : {plan['duration_hours']}h ({int(plan['total_minutes'])} minutes)")
    print(f"* Nombre total d'actions   : {plan['total_orders']} étapes espacées")
    print(f"* COUT TOTAL REEL          : ${plan['total_cost_usd']:.4f} USD")
    print("=" * 65)

    print("\n[+] COURBE DE PROGRESSION VIRALE (VUES CUMULEES) :")
    print(ascii_chart)
    print("\n" + "=" * 65)

    print("\n[+] EXTRAIT CHRONOLOGIQUE DES PREMIERES ETAPES :")
    print(f"{'Temps':<9} | {'Action':<14} | {'Service':<8} | {'Role algorithmique':<28} | {'Pause'}")
    print("-" * 65)
    for item in plan["timeline"][:7]:
        act = f"+{item['quantity']} {item['type']}"
        pause = f"{item['pause_min']} min" if item['pause_seconds'] > 0 else "Fin"
        print(f"{item['time_str']:<9} | {act:<14} | #{item['service_id']:<6} | {item['phase'][:28]:<28} | {pause}")

    print("  ...     |      ...       |  ...    |             ...            | ...")
    for item in plan["timeline"][-3:]:
        act = f"+{item['quantity']} {item['type']}"
        pause = f"{item['pause_min']} min" if item['pause_seconds'] > 0 else "Objectif"
        print(f"{item['time_str']:<9} | {act:<14} | #{item['service_id']:<6} | {item['phase'][:28]:<28} | {pause}")

    print("\n" + "=" * 65)
    print("[+] FICHIERS GENERES :")
    print(f"  1. Dashboard interactif HTML : {os.path.abspath(html_path)}")
    if HAS_MATPLOTLIB:
        print(f"  2. Graphique image PNG (3 courbes) : {os.path.abspath(png_path)}")
    print(f"  3. Plan complet JSON         : {os.path.abspath(json_path)}")
    print("=" * 65)

    if args.live:
        execute_live_run(plan, api_client, auto_confirm=args.yes)
    else:
        print("\n[i] MODE SIMULATION ACTIF (Aucun ordre reel envoye, aucun debit).")
        print("Pour lancer l'execution reelle sur le Reel :")
        print(f"  python boost_simulator.py --views {target_views} --hours {duration_hours} --link \"{args.link}\" --live\n")


if __name__ == "__main__":
    main()

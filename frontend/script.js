const analyzeBtn = document.getElementById('analyzeBtn')
const heroAnalyze = document.getElementById('heroAnalyze')
const modal = document.getElementById('modal')
const closeModalBtn = document.getElementById('closeModal')
const cancelBtn = document.getElementById('cancelBtn')
const backdrop = document.getElementById('backdrop')
const form = document.getElementById('analyzeForm')
const validationMessage = document.getElementById('validationMessage')
const dashboardSection = document.getElementById('reportDashboard')
const recommendationHeadline = document.getElementById('recommendationHeadline')
const explanationText = document.getElementById('explanationText')
const riskFill = document.getElementById('riskFill')
const trustScoreValue = document.getElementById('trustScoreValue')
const scamRiskLevelValue = document.getElementById('scamRiskLevelValue')
const scamRiskScoreValue = document.getElementById('scamRiskScoreValue')
const resumeMatchValue = document.getElementById('resumeMatchValue')
const opportunityScoreValue = document.getElementById('opportunityScoreValue')
const redFlagsContainer = document.getElementById('redFlagsContainer')
const matchingSkills = document.getElementById('matchingSkills')
const missingSkills = document.getElementById('missingSkills')
const matchingSkillsSection = document.getElementById('matchingSkillsSection')
const missingSkillsSection = document.getElementById('missingSkillsSection')
const skillsSection = document.getElementById('skillsSection')
const skillsFallback = document.getElementById('skillsFallback')
const viewAllFlagsButton = document.getElementById('viewAllFlagsButton')
const advisorText = document.getElementById('advisorText')
const improveText = document.getElementById('improveText')
const recommendationPanel = document.querySelector('.recommendation-panel')
const redFlagCount = document.getElementById('redFlagCount')

function openModal(source) {
  if (!modal) {
    console.warn('Modal element not found, cannot open modal')
    return
  }
  console.log('Analyze modal open clicked:', source)
  modal.setAttribute('aria-hidden', 'false')
  document.body.classList.add('modal-open')
}

function closeModal(clearForm = false) {
  if (!modal) return
  modal.setAttribute('aria-hidden', 'true')
  if (clearForm && form) {
    form.reset()
  }
  document.body.classList.remove('modal-open')
}

function mapRecommendationSummary(recommendation) {
  const text = String(recommendation || '').toLowerCase()
  if (text.includes('avoid')) {
    return 'High scam risk detected. Review red flags before taking action.'
  }
  if (text.includes('caution')) {
    return 'Some concerns found. Verify the opportunity before applying.'
  }
  return 'No major warning signs detected.'
}

function renderFlags(flags) {
  if (!redFlagsContainer) return
  redFlagsContainer.innerHTML = ''

  if (!Array.isArray(flags) || flags.length === 0) {
    const none = document.createElement('div')
    none.className = 'result-text'
    none.textContent = 'No red flags detected.'
    redFlagsContainer.appendChild(none)
    return
  }

  flags.forEach(flag => {
    const card = document.createElement('div')
    card.className = 'flag-card'
    const reasonSafe = flag.reason ? String(flag.reason) : ''
    card.innerHTML = `
      <h5>${flag.title}</h5>
      <span class="severity ${flag.severity.toLowerCase()}">${flag.severity}</span>
      <p>${reasonSafe}</p>
    `
    redFlagsContainer.appendChild(card)

    const p = card.querySelector('p')
    requestAnimationFrame(() => {
      if (p && p.scrollHeight > p.clientHeight + 2) {
        const btn = document.createElement('button')
        btn.type = 'button'
        btn.className = 'show-more'
        btn.textContent = 'Show details →'
        btn.addEventListener('click', () => {
          const expanded = card.classList.toggle('expanded')
          btn.textContent = expanded ? 'Show less' : 'Show details →'
        })
        card.appendChild(btn)
      }
    })
  })
}

function renderBadges(container, items) {
  if (!container) return false
  container.innerHTML = ''
  if (!Array.isArray(items) || items.length === 0) {
    return false
  }
  items.forEach(item => {
    const badge = document.createElement('span')
    badge.className = 'badge'
    badge.textContent = item
    container.appendChild(badge)
  })
  return true
}

function resetDashboardState() {
  if (validationMessage) validationMessage.hidden = true
  if (recommendationHeadline) recommendationHeadline.textContent = 'Safe to Apply'
  if (explanationText) explanationText.textContent = 'No major warning signs detected.'
  if (riskFill) riskFill.style.width = '0%'
  if (redFlagsContainer) redFlagsContainer.innerHTML = ''
  if (matchingSkills) matchingSkills.innerHTML = ''
  if (missingSkills) missingSkills.innerHTML = ''
  if (matchingSkillsSection) matchingSkillsSection.classList.remove('hidden')
  if (missingSkillsSection) missingSkillsSection.classList.remove('hidden')
  if (skillsSection) skillsSection.classList.add('hidden')
  if (advisorText) advisorText.textContent = 'This advice will help you act on the analysis.'
  if (improveText) improveText.textContent = 'Recommendations based on resume quality and skill gaps are shown here.'
  if (recommendationPanel) {
    recommendationPanel.classList.remove('recommendation-safe', 'recommendation-caution', 'recommendation-avoid')
    recommendationPanel.classList.add('recommendation-safe')
  }
}

function updateRecommendationPanel(result) {
  const recommendationText = String(result.recommendation || '').toLowerCase()
  if (recommendationPanel) {
    recommendationPanel.classList.remove('recommendation-safe', 'recommendation-caution', 'recommendation-avoid')
    if (recommendationText.includes('avoid')) {
      recommendationPanel.classList.add('recommendation-avoid')
    } else if (recommendationText.includes('caution')) {
      recommendationPanel.classList.add('recommendation-caution')
    } else {
      recommendationPanel.classList.add('recommendation-safe')
    }
  }
}

function updateScores(result) {
  if (trustScoreValue) trustScoreValue.textContent = `${result.trust_score}/100`
  if (scamRiskLevelValue) scamRiskLevelValue.textContent = result.scam_risk_level || ''
  if (scamRiskScoreValue) scamRiskScoreValue.textContent = `${result.scam_risk_score}/100`
  if (recommendationHeadline) recommendationHeadline.textContent = result.recommendation || ''
  if (explanationText) explanationText.textContent = mapRecommendationSummary(result.recommendation)
  if (resumeMatchValue) resumeMatchValue.textContent = `${Number(result.resume_match_score).toFixed(2)}%`
  if (opportunityScoreValue) opportunityScoreValue.textContent = `${Number(result.opportunity_score).toFixed(2)}/100`

  const riskPercent = Math.min(100, Math.max(0, result.scam_risk_score || 0))
  if (riskFill) riskFill.style.width = `${riskPercent}%`
  if (riskFill) {
    if (riskPercent <= 30) {
      riskFill.style.background = 'linear-gradient(90deg, #44ff96, #7effd0)'
    } else if (riskPercent <= 65) {
      riskFill.style.background = 'linear-gradient(90deg, #ffd86a, #ffa86e)'
    } else {
      riskFill.style.background = 'linear-gradient(90deg, #ff6f6f, #ff3e5f)'
    }
  }
}

function updateFlags(result) {
  const allFlags = Array.isArray(result.red_flags) ? result.red_flags : []
  let showingAllFlags = false
  const maxVisibleFlags = 4

  const refresh = () => {
    const visible = showingAllFlags ? allFlags : allFlags.slice(0, maxVisibleFlags)
    renderFlags(visible)
    if (viewAllFlagsButton) {
      if (allFlags.length > maxVisibleFlags) {
        viewAllFlagsButton.classList.remove('hidden')
        viewAllFlagsButton.textContent = showingAllFlags
          ? 'Show fewer'
          : `View all red flags (${allFlags.length})`
      } else {
        viewAllFlagsButton.classList.add('hidden')
      }
    }
    if (redFlagCount) redFlagCount.textContent = allFlags.length
  }

  if (viewAllFlagsButton) {
    viewAllFlagsButton.onclick = () => {
      showingAllFlags = !showingAllFlags
      refresh()
    }
  }

  refresh()
}

function updateSkills(result) {
  const matchingVisible = renderBadges(matchingSkills, result.matching_skills)
  const missingVisible = renderBadges(missingSkills, result.missing_skills)

  if (matchingSkillsSection) {
    matchingSkillsSection.classList.toggle('hidden', !matchingVisible)
  }
  if (missingSkillsSection) {
    missingSkillsSection.classList.toggle('hidden', !missingVisible)
  }
  if (skillsSection) {
    skillsSection.classList.toggle('hidden', !matchingVisible && !missingVisible)
  }
  if (skillsFallback) {
    skillsFallback.classList.toggle('hidden', matchingVisible || missingVisible)
  }
}

function updateAdvice(result) {
  let advisorTextValue = ''
  const recommendationText = String(result.recommendation || '').toLowerCase()
  const flagLabels = Array.isArray(result.red_flags)
    ? result.red_flags.slice(0, 3).map(flag => flag.title.toLowerCase()).join(', ')
    : ''

  if (recommendationText.includes('avoid')) {
    advisorTextValue = flagLabels
      ? `Avoid this opportunity. It contains serious warning signs such as ${flagLabels}. Apply only through verified company portals.`
      : 'Avoid this opportunity. It contains warning signs. Apply only through verified company portals.'
  } else if (recommendationText.includes('caution')) {
    advisorTextValue = 'Verify the company website, recruiter email, and job details before applying.'
  } else {
    advisorTextValue = 'This opportunity appears safe based on available information. Still verify the company website before sharing personal documents.'
  }

  if (advisorText) advisorText.textContent = advisorTextValue
}

function updateImprovements(result) {
  const suggestions = []
  if (Array.isArray(result.missing_skills) && result.missing_skills.length > 0) {
    result.missing_skills.slice(0, 3).forEach(skill => {
      suggestions.push(`Learn or highlight ${skill} before applying.`)
    })
  }
  if (Number(result.resume_match_score) < 50) {
    suggestions.push('Your resume match is low. Customize your resume with relevant skills and project keywords.')
  }
  if (suggestions.length === 0) {
    suggestions.push('Your resume alignment is strong. Focus on verified company details and job quality.')
  }
  if (improveText) {
    improveText.innerHTML = suggestions.map(line => `<p>${line}</p>`).join('')
  }
}

async function handleSubmit(event) {
  event.preventDefault()
  console.log('Run Analysis clicked')
  if (!form) return

  const data = Object.fromEntries(new FormData(form).entries())
  const payload = {
    job_text: data.job_text || '',
    recruiter_message: data.recruiter_message || '',
    email: data.email || '',
    salary: data.salary || '',
    resume_text: data.resume_text || ''
  }

  if (!payload.job_text.trim()) {
    if (validationMessage) {
      validationMessage.textContent = 'Please enter at least a job description.'
      validationMessage.hidden = false
    }
    return
  }

  resetDashboardState()
  if (dashboardSection) dashboardSection.classList.add('hidden')

  console.log('Sending generate-report payload:', payload)
  try {
    const response = await fetch('http://127.0.0.1:8000/generate-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      if (validationMessage) {
        validationMessage.textContent = `Error ${response.status}: ${response.statusText || 'Network error'}`
        validationMessage.hidden = false
      }
      return
    }

    const result = await response.json()
    updateScores(result)
    updateRecommendationPanel(result)
    updateFlags(result)
    updateSkills(result)
    updateAdvice(result)
    updateImprovements(result)

    if (validationMessage) {
      validationMessage.textContent = ''
      validationMessage.hidden = true
    }
    if (dashboardSection) dashboardSection.classList.remove('hidden')
    closeModal(true)
    if (dashboardSection) {
      dashboardSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  } catch (error) {
    console.error('generate-report request failed:', error)
    if (validationMessage) {
      validationMessage.textContent = error instanceof TypeError
        ? 'Backend is not running. Please start FastAPI server.'
        : String(error)
      validationMessage.hidden = false
    }
  }
}

function handleDownloadReport() {
  const getText = (id) => document.getElementById(id)?.textContent?.trim() || ''
  const recommendation = getText('recommendationHeadline')
  const trust = getText('trustScoreValue')
  const scam = getText('scamRiskScoreValue')
  const resumeMatch = getText('resumeMatchValue')
  const oppScore = getText('opportunityScoreValue')
  const advisor = getText('advisorText')

  let improvements = ''
  const improveEl = document.getElementById('improveText')
  if (improveEl) {
    const parts = Array.from(improveEl.querySelectorAll('p'))
      .map(p => p.textContent.trim())
      .filter(Boolean)
    improvements = parts.join('\n') || improveEl.textContent.trim()
  }

  const rfContainer = document.getElementById('redFlagsContainer')
  let redFlags = []
  if (rfContainer) {
    const cards = Array.from(rfContainer.querySelectorAll('.flag-card'))
    if (cards.length === 0) {
      const none = rfContainer.querySelector('.result-text')
      if (none) redFlags = [none.textContent.trim()]
    } else {
      redFlags = cards.map(c => {
        const title = c.querySelector('h5')?.textContent?.trim() || ''
        const sev = c.querySelector('.severity')?.textContent?.trim() || ''
        const reason = c.querySelector('p')?.textContent?.trim() || ''
        return `${title}${sev ? ' [' + sev + ']' : ''}${reason ? ': ' + reason : ''}`
      })
    }
  }

  const matching = Array.from(document.getElementById('matchingSkills')?.querySelectorAll('.badge') || [])
    .map(e => e.textContent.trim())
    .filter(Boolean)
  const missing = Array.from(document.getElementById('missingSkills')?.querySelectorAll('.badge') || [])
    .map(e => e.textContent.trim())
    .filter(Boolean)

  const recText = (recommendation || '').toLowerCase()
  let recColor = '#2ecc71'
  if (recText.includes('avoid')) recColor = '#ff6b6b'
  else if (recText.includes('caution')) recColor = '#ffcc66'

  const title = 'CareerShield_Report'
  const html = `<!doctype html>
      <html>
      <head>
        <meta charset="utf-8" />
        <title>${title}</title>
        <style>
          body{font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Arial; color:#0b1220; margin:28px}
          .header{display:flex;align-items:center;gap:12px}
          .brand{font-weight:800;font-size:20px}
          .accent{color:${recColor};font-weight:700}
          .section{margin-top:18px}
          h2{margin:6px 0 8px;font-size:16px}
          .metric{display:flex;justify-content:space-between;padding:10px 12px;background:#f6f8fa;border-radius:8px;margin-bottom:8px}
          .muted{color:#6b7280}
          .badge{display:inline-block;padding:6px 10px;border-radius:999px;background:#eef2f6;margin:6px 6px 0 0}
          .red-flag{background:#fff3f3;border-left:4px solid #ff6b6b;padding:8px;border-radius:6px;margin-bottom:8px}
        </style>
      </head>
      <body>
        <div class="header">
          <div class="brand">CareerShield <span class="accent">AI</span></div>
        </div>
        <div class="section">
          <h2>Recommendation</h2>
          <div class="metric"><strong style="color:${recColor}">${recommendation}</strong><span class="muted">${new Date().toLocaleString()}</span></div>
        </div>
        <div class="section">
          <h2>Scores</h2>
          <div class="metric"><span>Trust Score</span><strong>${trust}</strong></div>
          <div class="metric"><span>Scam Risk Score</span><strong>${scam}</strong></div>
          <div class="metric"><span>Resume Match</span><strong>${resumeMatch}</strong></div>
          <div class="metric"><span>Opportunity Score</span><strong>${oppScore}</strong></div>
        </div>
        <div class="section">
          <h2>Red Flags</h2>
          ${redFlags.length ? redFlags.map(f => `<div class="red-flag">${f}</div>`).join('') : '<div class="muted">None detected.</div>'}
        </div>
        ${matching.length ? `<div class="section"><h2>Matching Skills</h2><div>${matching.map(s=>`<span class="badge">${s}</span>`).join('')}</div></div>` : ''}
        ${missing.length ? `<div class="section"><h2>Missing Skills</h2><div>${missing.map(s=>`<span class="badge">${s}</span>`).join('')}</div></div>` : ''}
        <div class="section">
          <h2>AI Career Advisor</h2>
          <div class="muted">${advisor}</div>
        </div>
        <div class="section">
          <h2>Improvement Suggestions</h2>
          <div class="muted">${improvements.split('\n').map(l=>`<div>${l}</div>`).join('')}</div>
        </div>
      </body>
      </html>`

  const win = window.open('', '_blank')
  if (!win) {
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'CareerShield_Report.html'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    return
  }
  win.document.open()
  win.document.write(html)
  win.document.close()
  try { win.document.title = 'CareerShield_Report' } catch (e) {}
  setTimeout(() => { try { win.focus(); win.print(); } catch (e) { /* ignore */ } }, 300)
}

function initialize() {
  if (!form) {
    console.warn('Analyze form not found')
    return
  }
  if (analyzeBtn) {
    analyzeBtn.type = 'button'
    analyzeBtn.addEventListener('click', (e) => {
      e.preventDefault()
      openModal('header')
    })
  }
  if (heroAnalyze) {
    heroAnalyze.type = 'button'
    heroAnalyze.addEventListener('click', (e) => {
      e.preventDefault()
      openModal('hero')
    })
  }
  if (closeModalBtn) {
    closeModalBtn.type = 'button'
    closeModalBtn.addEventListener('click', (e) => {
      e.preventDefault()
      closeModal(false)
    })
  }
  if (cancelBtn) {
    cancelBtn.type = 'button'
    cancelBtn.addEventListener('click', (e) => {
      e.preventDefault()
      closeModal(false)
    })
  }
  if (backdrop) {
    backdrop.addEventListener('click', () => closeModal(false))
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal?.getAttribute('aria-hidden') === 'false') {
      closeModal(false)
    }
  })
  form.addEventListener('submit', handleSubmit)

  const downloadBtn = document.getElementById('downloadReportBtn')
  if (downloadBtn) {
    downloadBtn.addEventListener('click', handleDownloadReport)
  }
}

initialize()

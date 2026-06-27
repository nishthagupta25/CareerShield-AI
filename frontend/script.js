let latestAnalysisResult = null
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
const runAnalysisBtn = document.getElementById('runAnalysisBtn')

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

function mapRecommendationSummary(result) {
  if (result.recommendation === 'Insufficient Data') {
    return 'Please provide complete job and resume details to generate meaningful insights.'
  }

  if (result.recommendation === 'Needs Resume Review') {
    return 'Job safety was checked, but your resume needs more meaningful information.'
  }

  const text = String(result.recommendation || '').toLowerCase()

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
  if (runAnalysisBtn) {
  runAnalysisBtn.disabled = true
  runAnalysisBtn.classList.add('loading')
}
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
    recommendationPanel.classList.remove(
      'recommendation-safe',
      'recommendation-caution',
      'recommendation-avoid',
      'recommendation-neutral'
    )

    if (recommendationText.includes('insufficient') || recommendationText.includes('resume review')) {
      recommendationPanel.classList.add('recommendation-neutral')
    } else if (recommendationText.includes('avoid')) {
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
  if (explanationText) explanationText.textContent = mapRecommendationSummary(result)
  if (resumeMatchValue) {
  resumeMatchValue.textContent = result.resume_input_valid === false
    ? 'Insufficient Data'
    : `${Number(result.resume_match_score).toFixed(2)}%`
}
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

  if (recommendationText.includes('insufficient')) {
    advisorTextValue =
      'Career advice is unavailable because the job or resume information is not enough for analysis.'
  } else if (result.resume_input_valid === false) {
    advisorTextValue =
      'CareerShield can check the job safety, but your resume does not contain enough meaningful information for personalized career advice.'
  } else if (recommendationText.includes('avoid')) {
    advisorTextValue =
      'Avoid this opportunity. It contains serious warning signs. Apply only through verified company portals.'
  } else if (recommendationText.includes('caution')) {
    advisorTextValue =
      'Verify the company website, recruiter email, and job details before applying.'
  } else {
    advisorTextValue =
      'This opportunity appears safe based on available information. Still verify the company website before sharing personal documents.'
  }

  if (advisorText) advisorText.textContent = advisorTextValue
}
function updateImprovements(result) {
  if (result.recommendation === 'Insufficient Data') {
    if (improveText) {
      improveText.innerHTML =
        '<p>Add a complete job description and resume to receive improvement suggestions.</p>'
    }
    return
  }

  if (result.resume_input_valid === false) {
    if (improveText) {
      improveText.innerHTML =
        '<p>Add a complete resume with skills, projects, education, and experience to receive personalized suggestions.</p>'
    }
    return
  }

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

function updateCareerIntelligence(result) {
  const section = document.getElementById('careerIntelligenceSection')
  if (!section) return

  const verdict = document.getElementById('aiCareerVerdict')
  const recruiter = document.getElementById('aiRecruiterView')
  const readiness = document.getElementById('interviewReadinessScore')
  const roadmapList = document.getElementById('skillRoadmapList')
  const questionsList = document.getElementById('interviewQuestionsList')
  const whySafeList = document.getElementById('aiWhySafeList')
  const whyAttentionList = document.getElementById('aiWhyAttentionList')
  const finalSummary = document.getElementById('aiFinalSummary')
  section.classList.remove('hidden')

  if (verdict) verdict.textContent = result.ai_career_verdict || 'No career verdict available.'
  if (recruiter) recruiter.textContent = result.ai_recruiter_view || 'No recruiter view available.'
  if (readiness) readiness.textContent = `${result.interview_readiness_score || 0}%`

  if (roadmapList) {
    roadmapList.innerHTML = ''
    ;(result.skill_roadmap || []).forEach(item => {
      const li = document.createElement('li')
      li.textContent = item
      roadmapList.appendChild(li)
    })
  }

  if (questionsList) {
    questionsList.innerHTML = ''
    ;(result.likely_interview_questions || []).forEach(question => {
      const li = document.createElement('li')
      li.textContent = question
      questionsList.appendChild(li)
    })
  }
  const explanation = result.ai_explanation || {}

if (whySafeList) {
  whySafeList.innerHTML = ''
  ;(explanation.why_safe || []).forEach(item => {
    const li = document.createElement('li')
    li.textContent = `✅ ${item}`
    whySafeList.appendChild(li)
  })
}

if (whyAttentionList) {
  whyAttentionList.innerHTML = ''
  ;(explanation.why_attention || []).forEach(item => {
    const li = document.createElement('li')
    li.textContent = `⚠️ ${item}`
    whyAttentionList.appendChild(li)
  })
}

if (finalSummary) {
  finalSummary.textContent = explanation.final_summary || ''
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
  if (runAnalysisBtn) {
  runAnalysisBtn.textContent = 'Analyzing...'
}
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
    latestAnalysisResult = result
    updateScores(result)
    updateRecommendationPanel(result)
    updateFlags(result)
    updateSkills(result)
    updateAdvice(result)
    updateImprovements(result)
    updateCareerIntelligence(result)

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
  } finally {
    if (runAnalysisBtn) {
      runAnalysisBtn.textContent = 'Run Analysis'
      runAnalysisBtn.disabled = false
      runAnalysisBtn.classList.remove('loading')
    }
  }
}
function handleDownloadReport() {
  if (!latestAnalysisResult) {
    alert('Please run an analysis first.')
    return
  }

  const { jsPDF } = window.jspdf
  const doc = new jsPDF()
  const result = latestAnalysisResult

  const pageWidth = doc.internal.pageSize.getWidth()
  const margin = 14
  let y = 18

  const checkPage = () => {
    if (y > 268) {
      doc.addPage()
      y = 18
    }
  }

  const addSection = (title) => {
    checkPage()
    y += 5
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(13)
    doc.setTextColor(24, 52, 105)
    doc.text(title, margin, y)
    y += 8
  }

  const addText = (text) => {
    checkPage()
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(55, 65, 80)
    const lines = doc.splitTextToSize(String(text || ''), pageWidth - margin * 2)
    doc.text(lines, margin, y)
    y += lines.length * 5 + 3
  }

  const addBullet = (text) => {
    checkPage()
    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)
    doc.setTextColor(55, 65, 80)
    const lines = doc.splitTextToSize(`• ${text}`, pageWidth - margin * 2)
    doc.text(lines, margin, y)
    y += lines.length * 5 + 2
  }

  

  const addRedFlag = (flag) => {
    checkPage()
    const severity = String(flag.severity || 'warning').toUpperCase()

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(210, 65, 65)
    doc.text(severity, margin, y)
    y += 5

    doc.setFontSize(10)
    doc.setTextColor(25, 35, 55)
    doc.text(String(flag.title || 'Warning sign'), margin, y)
    y += 5

    doc.setFont('helvetica', 'normal')
    doc.setTextColor(55, 65, 80)
    const reasonLines = doc.splitTextToSize(String(flag.reason || ''), pageWidth - margin * 2)
    doc.text(reasonLines, margin, y)
    y += reasonLines.length * 5 + 4

    doc.setTextColor(95, 105, 120)
    const whyLines = doc.splitTextToSize(
      'Why it matters: Genuine companies usually do not ask for money, urgent payments, or unverifiable personal details before hiring.',
      pageWidth - margin * 2
    )
    doc.text(whyLines, margin, y)
    y += whyLines.length * 5 + 5
  }

  // Header
  doc.setFillColor(12, 18, 32)
  doc.rect(0, 0, pageWidth, 34, 'F')

  doc.setTextColor(255, 255, 255)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(18)
  doc.text('CareerShield AI', margin, 18)

  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('AI Job Opportunity Report', margin, 26)

  y = 46

  const verdict = result.recommendation || 'N/A'
  const scamRisk = Number(result.scam_risk_score || 0)
  const resumeMatch = Number(result.resume_match_score || 0)
  const opportunityScore = Number(result.opportunity_score || 0)
  const readinessScore = Number(result.interview_readiness_score || 0)

  let verdictColor = [46, 204, 113]
  if (String(verdict).toLowerCase().includes('avoid') || scamRisk >= 70) {
    verdictColor = [231, 76, 60]
  } else if (String(verdict).toLowerCase().includes('caution') || scamRisk >= 35) {
    verdictColor = [243, 156, 18]
  }

  // Recommendation Box
  doc.setFillColor(245, 248, 252)
  doc.roundedRect(margin, y, pageWidth - margin * 2, 64, 5, 5, 'F')

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(13)
  doc.setTextColor(20, 30, 50)
  doc.text('Final Recommendation', margin + 6, y + 11)

  doc.setFontSize(20)
  doc.setTextColor(...verdictColor)
  doc.text(verdict.toUpperCase(), margin + 6, y + 29)

  doc.setFontSize(10)
  doc.setTextColor(55, 65, 80)
  doc.text(`Opportunity Score: ${opportunityScore.toFixed(2)}/100`, margin + 6, y + 43)
  doc.text(`Scam Risk: ${result.scam_risk_level || 'Low'}`, margin + 6, y + 54)
  doc.text(`Resume Match: ${resumeMatch.toFixed(2)}%`, margin + 74, y + 54)
  doc.text(`Interview Readiness: ${readinessScore}%`, margin + 138, y + 54)

  y += 76

  addSection('Key Reasons Behind This Recommendation')

  const safePoints = result.ai_explanation?.why_safe || []
  const attentionPoints = result.ai_explanation?.why_attention || []

  if (safePoints.length) {
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.setTextColor(35,120,80)
    doc.text("What's Good", margin, y)
    y += 6

    safePoints.slice(0,4).forEach(item => {
        addBullet(item)
    })
}

  if (attentionPoints.length) {
    y += 2

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.setTextColor(190,120,30)
    doc.text("Before You Apply", margin, y)
    y += 6

    attentionPoints.slice(0,4).forEach(item=>{
        addBullet(item)
    })
}

  addSection("Career Insights")
  addText(result.ai_recruiter_view || result.ai_career_verdict || 'No career advice available.')

  addSection('Skills You Already Have')
  const matching = result.matching_skills || []
  if (matching.length) {
    matching.slice(0,10).forEach(skill=>{
    addBullet(skill)
})
  } else {
    addText('No matching skills detected.')
  }

  addSection('Skills That Can Improve Your Chances')
  const missing = result.missing_skills || []
  if (missing.length) {
    missing.slice(0,8).forEach(skill=>{
    addBullet(skill)
})
  } else {
    addText('No major missing skills detected.')
  }

  addSection('Next Steps')
  const roadmap = result.skill_roadmap || []
  if (roadmap.length) {
    roadmap.slice(0, 5).forEach(item => addBullet(item))
  } else {
    addBullet('Verify the company website before applying.')
    addBullet('Apply only through official company portals.')
    addBullet('Never pay registration or processing fees.')
  }

  addSection('Possible Interview Questions')
  const questions = result.likely_interview_questions || []
  if (questions.length) {
    questions.slice(0, 5).forEach(q => addBullet(q))
  } else {
    addText('No interview questions generated.')
  }

  addSection('Warning Signs Detected')
  if (Array.isArray(result.red_flags) && result.red_flags.length > 0) {
    result.red_flags.forEach(flag => addRedFlag(flag))
  } else {
    addText('No major warning signs were detected.')
  }

  addSection('Safety Checklist Before Applying')
  addBullet('Verify the company website and recruiter identity.')
addBullet('Apply only through official company portals.')
addBullet('Never pay money for an interview, offer letter, or onboarding.')
addBullet('Never share OTP, bank details, or sensitive documents before verification.')

  addSection('Disclaimer')
  addText(
    'This report is automatically generated by CareerShield AI to help job seekers identify recruitment scams and prepare better for genuine opportunities. It is advisory and should be used along with personal verification.'
  )

  doc.setFontSize(8)
  doc.setTextColor(120, 120, 120)
  doc.text(`Generated by CareerShield AI on ${new Date().toLocaleString()}`, margin, 287)

  doc.save('CareerShield_AI_Report.pdf')
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
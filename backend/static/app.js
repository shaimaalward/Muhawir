const STORAGE = {
  profile: "muhawir_profile_v2",
  history: "muhawir_history_v2"
};


/* =========================================================
   PERSONAS
   ========================================================= */

const PERSONAS = [
  {
    id: "adam",
    name: "آدم",
    className: "adam",
    image: "adam.png",
    description:
      "شخصية ودودة وفضولية، تفضّل الأمثلة اليومية والشرح البسيط وتتفاعل بطبيعية دون تحويل الحوار إلى أسئلة متتابعة.",
    tags: [
      "ودود",
      "عملي",
      "أمثلة يومية"
    ]
  },

  {
    id: "maya",
    name: "مايا",
    className: "maya",
    image: "maya.png",
    description:
      "شخصية تحليلية ودقيقة، تركّز على المنطق والأدلة وتلاحظ الافتراضات والتناقضات وتطلب توضيحًا عند الحاجة.",
    tags: [
      "تحليلية",
      "دقيقة",
      "تركّز على الأدلة"
    ]
  }
];


function topic(
  id,
  title,
  description,
  opening
) {
  return {
    id,
    title,
    description,
    opening
  };
}


/* =========================================================
   TOPICS
   ========================================================= */

const TOPIC_GROUPS = [

  {
    title: "العقيدة والإيمان",

    topics: [

      topic(
        "who_is_allah",
        "من هو الله",
        "كيف يعرّف الإسلام بالله؟",
        "أسمع المسلمين يتحدثون كثيرًا عن الله. من هو الله في الإسلام ببساطة؟"
      ),

      topic(
        "tawhid",
        "التوحيد",
        "ما معنى توحيد الله؟",
        "أسمع كلمة التوحيد كثيرًا. ماذا تعني لشخص لا يعرف المصطلح؟"
      ),

      topic(
        "six_pillars_faith",
        "أركان الإيمان",
        "ما الذي يؤمن به المسلم؟",
        "ما أهم الأشياء التي يجب على المسلم أن يؤمن بها؟"
      ),

      topic(
        "qadar",
        "القضاء والقدر",
        "كيف يفهم الإسلام القدر والاختيار؟",
        "إذا كان كل شيء مقدرًا، فهل الإنسان يملك اختيارًا فعلًا؟"
      )

    ]
  },


  {
    title: "القرآن الكريم",

    topics: [

      topic(
        "quran",
        "ما هو القرآن",
        "تعريف القرآن ومكانته في الإسلام.",
        "ما هو القرآن بالضبط؟ ولماذا يعتبره المسلمون مختلفًا عن أي كتاب آخر؟"
      ),

      topic(
        "quran_revelation",
        "نزول القرآن والوحي",
        "كيف نزل القرآن وما معنى الوحي؟",
        "كيف يقول المسلمون إن القرآن نزل من عند الله؟ ماذا يعني الوحي أصلًا؟"
      ),

      topic(
        "quran_preservation",
        "حفظ القرآن",
        "كيف حُفظ القرآن عبر التاريخ؟",
        "سمعت أن القرآن جُمع بعد وفاة النبي. كيف يقول المسلمون إنه محفوظ؟"
      ),

      topic(
        "quran_science",
        "القرآن والعلم",
        "كيف يفهم المسلم العلاقة بين القرآن والعلم؟",
        "أحيانًا أسمع أن القرآن يحتوي على حقائق علمية. كيف يفهم المسلمون هذا الموضوع؟"
      )

    ]
  },


  {
    title: "الأنبياء والرسل",

    topics: [

      topic(
        "prophets",
        "الأنبياء والرسل",
        "لماذا أرسل الله الأنبياء؟",
        "لماذا احتاج الناس إلى أنبياء ورسل أصلًا؟"
      ),

      topic(
        "jesus_in_islam",
        "عيسى عليه السلام في الإسلام",
        "مكانة عيسى عليه السلام في الإسلام.",
        "أنا أعرف عيسى من المسيحية. كيف ينظر إليه الإسلام؟"
      ),

      topic(
        "prophet_muhammad",
        "النبي محمد صلى الله عليه وسلم",
        "من هو النبي محمد وما رسالته؟",
        "من هو محمد بالنسبة للمسلمين؟ ولماذا يؤمنون بأنه نبي؟"
      )

    ]
  },


  {
    title: "العبادات",

    topics: [

      topic(
        "five_pillars",
        "أركان الإسلام",
        "ما الممارسات الأساسية في الإسلام؟",
        "ما هي أركان الإسلام؟ وهل كلها عبادات يومية؟"
      ),

      topic(
        "prayer",
        "الصلاة",
        "لماذا وكيف يصلي المسلمون؟",
        "إذا كان الله يعلم كل شيء، فلماذا يحتاج المسلم أن يصلي خمس مرات؟"
      ),

      topic(
        "ramadan_fasting",
        "الصيام",
        "ما معنى الصيام في رمضان؟",
        "لماذا يصوم المسلمون شهرًا كاملًا في رمضان؟"
      ),

      topic(
        "zakat",
        "الزكاة",
        "لماذا الزكاة عبادة وحق مالي؟",
        "ما الفرق بين الزكاة والصدقة العادية؟"
      )

    ]
  },


  {
    title: "الحج والعمرة",

    topics: [

      topic(
        "hajj",
        "الحج",
        "ما معنى الحج ولماذا يؤديه المسلم؟",
        "لماذا يذهب المسلمون إلى مكة للحج؟ وما الذي يمثله لهم؟"
      ),

      topic(
        "umrah",
        "العمرة",
        "ما الفرق بين العمرة والحج؟",
        "أسمع عن الحج والعمرة. ما الفرق بينهما؟"
      ),

      topic(
        "kaaba_qiblah",
        "الكعبة والقبلة",
        "لماذا يتجه المسلمون إلى الكعبة في الصلاة؟",
        "كنت أسمع أن المسلمين في كل مكان يتجهون نحو الكعبة أثناء الصلاة. لماذا يفعلون ذلك؟"
      )

    ]
  },


  {
    title: "المرأة في الإسلام",

    topics: [

      topic(
        "women_in_islam",
        "المرأة في الإسلام",
        "كيف يقدّم الإسلام مكانة المرأة؟",
        "ما مكانة المرأة في الإسلام بشكل عام؟"
      ),

      topic(
        "hijab",
        "الحجاب",
        "لماذا ترتدي بعض المسلمات الحجاب؟",
        "لماذا ترتدي المسلمات الحجاب؟ وهل هو اختيار أم فرض؟"
      ),

      topic(
        "women_rights_islam",
        "حقوق المرأة في الإسلام",
        "ما الحقوق التي يقررها الإسلام للمرأة؟",
        "عندما يتحدث الناس عن حقوق المرأة في الإسلام، ما الحقوق التي يقصدونها؟"
      )

    ]
  },


  {
    title: "مواضيع أخرى",

    topics: [

      topic(
        "purpose_of_life",
        "غاية الحياة في الإسلام",
        "لماذا خلق الإنسان وما غاية حياته؟",
        "ما إجابة الإسلام عن سؤال: لماذا نحن هنا أصلًا؟"
      ),

      topic(
        "jihad",
        "الجهاد في الإسلام",
        "ما معنى الجهاد بعيدًا عن الصور الشائعة؟",
        "كلمة الجهاد ترتبط عند كثير من الناس بالعنف. ماذا تعني في الإسلام؟"
      ),

      topic(
        "islam_spread",
        "انتشار الإسلام",
        "كيف يشرح المسلم تاريخ انتشار الإسلام؟",
        "هل صحيح أن الإسلام انتشر فقط بالقوة والسيف؟"
      )

    ]
  }

];


const TOPICS =
  TOPIC_GROUPS.flatMap(
    group => group.topics
  );


/* =========================================================
   SKILLS
   ========================================================= */

const SKILLS = [

  {
    key: "accuracy",
    label: "دقة المعلومات"
  },

  {
    key: "evidence",
    label: "الاستدلال بالمصادر"
  },

  {
    key: "clarity",
    label: "وضوح الشرح"
  },

  {
    key: "listening",
    label: "الاستماع والاستجابة"
  },

  {
    key: "wisdom",
    label: "الحكمة والأسلوب"
  },

  {
    key: "structure",
    label: "تنظيم الإجابة"
  },

  {
    key: "voice",
    label: "الأداء الصوتي"
  }

];


const SKILL_STRENGTH_COPY = {

  accuracy:
    "تقدّم معلومات دقيقة ومتوافقة مع المصادر المعتمدة.",

  evidence:
    "تستخدم الأدلة في مواضع مناسبة وتربطها بالفكرة التي تشرحها.",

  clarity:
    "تشرح الأفكار بلغة واضحة وبسيطة يسهل على الطرف الآخر فهمها.",

  listening:
    "تستجيب لما يقصده الطرف الآخر وتبني إجابتك على سؤاله مباشرة.",

  wisdom:
    "تتعامل مع الأسئلة بهدوء واحترام وتوضح الأفكار دون مواجهة غير ضرورية.",

  structure:
    "ترتب أفكارك بطريقة تجعل الإجابة سهلة المتابعة.",

  voice:
    "حديثك واضح ووتيرتك تساعد على فهم ما تقوله."

};


const SKILL_FOCUS_COPY = {

  accuracy:
    "تحقق من المعلومة قبل التوسع في الشرح أو ذكر تفاصيل إضافية.",

  evidence:
    "استخدم دليلًا واضحًا عند الحاجة واشرح علاقته بالفكرة.",

  clarity:
    "ابدأ بالمعنى البسيط ثم وضّح المصطلحات الإسلامية عند استخدامها.",

  listening:
    "اجعل ردك مرتبطًا مباشرة بآخر سؤال أو اعتراض طرحه الطرف الآخر.",

  wisdom:
    "حافظ على هدوء اللغة ووضّح الفكرة دون أن يشعر الطرف الآخر بأنه يتعرض للتوبيخ.",

  structure:
    "ابدأ بجواب مباشر ثم شرح مختصر ثم دليل عند الحاجة.",

  voice:
    "حافظ على سرعة حديث مريحة وتجنب التوقفات الطويلة."

};


const SESSION_GUIDANCE = {

  accuracy: [
    "تحقق قبل أن تتوسع",
    "إذا لم تكن متأكدًا من تفصيل شرعي، لا تقدمه بصيغة الجزم."
  ],

  evidence: [
    "اختر الدليل المناسب",
    "استخدم الدليل عندما يخدم الفكرة وبيّن علاقته بما تقوله."
  ],

  clarity: [
    "بسّط المصطلح",
    "ابدأ بالمعنى البسيط ثم استخدم المصطلح بعد توضيحه."
  ],

  listening: [
    "استمع للسؤال",
    "ابدأ بالإجابة عما قصده الطرف الآخر قبل إضافة تفاصيل أخرى."
  ],

  wisdom: [
    "صحح بلطف",
    "يمكنك تصحيح الفكرة دون إحراج الطرف الآخر."
  ],

  structure: [
    "رتب إجابتك",
    "جواب مباشر ثم شرح مختصر ثم دليل عند الحاجة."
  ],

  voice: [
    "تحدث بوتيرة مريحة",
    "خذ توقفات طبيعية وتجنب الاستعجال."
  ]

};


/* =========================================================
   PAGES
   ========================================================= */

const pages = {

  dashboard:
    document.getElementById(
      "dashboardPage"
    ),

  training:
    document.getElementById(
      "trainingPage"
    ),

  persona:
    document.getElementById(
      "personaPage"
    ),

  conversation:
    document.getElementById(
      "conversationPage"
    ),

  feedback:
    document.getElementById(
      "feedbackPage"
    ),

  history:
    document.getElementById(
      "historyPage"
    ),

  "session-detail":
    document.getElementById(
      "sessionDetailPage"
    ),

  profile:
    document.getElementById(
      "profilePage"
    )

};


/* =========================================================
   STATE
   ========================================================= */

let profile =
  loadJSON(
    STORAGE.profile,
    null
  );


let history =
  loadJSON(
    STORAGE.history,
    []
  );


if (!Array.isArray(history)) {
  history = [];
}


let selectedPersona =
  PERSONAS[0];


let selectedTopic =
  TOPICS.find(
    item =>
      item.id ===
      "kaaba_qiblah"
  ) ||
  TOPICS[0];


let selectedHistoryId =
  null;


let currentSessionId =
  null;


let currentTranscript =
  [];


let currentEvaluation =
  null;


let sessionStartedAt =
  null;


let timerHandle =
  null;


let mediaRecorder =
  null;


let currentStream =
  null;


let audioChunks =
  [];


let mimeType =
  "";


let recording =
  false;


let requestInProgress =
  false;


let personaAudio =
  null;


let toastHandle =
  null;


/* =========================================================
   START
   ========================================================= */

document.addEventListener(
  "DOMContentLoaded",
  () => {

    bindEvents();

    renderPersonas();

    renderTopicGroups();

    renderDashboard();

    renderHistory();

    updateProfileUI();


    setTimeout(
      () => {

        document
          .getElementById(
            "splashScreen"
          )
          .classList
          .add(
            "hidden"
          );


        if (profile?.name) {

          document
            .getElementById(
              "appRoot"
            )
            .classList
            .remove(
              "hidden"
            );

          navigate(
            "dashboard"
          );

        } else {

          document
            .getElementById(
              "authScreen"
            )
            .classList
            .remove(
              "hidden"
            );

        }

      },
      700
    );

  }
);


/* =========================================================
   EVENTS
   ========================================================= */

function bindEvents() {

  document.addEventListener(
    "click",
    event => {

      const routeButton =
        event.target.closest(
          "[data-route]"
        );


      if (!routeButton) {
        return;
      }


      const route =
        routeButton.dataset.route;


      if (
        recording &&
        route !==
        "conversation"
      ) {

        showToast(
          "أوقف التسجيل أولًا."
        );

        return;
      }


      if (
        route ===
        "dashboard"
      ) {

        renderDashboard();

      }


      if (
        route ===
        "training"
      ) {

        renderPersonas();

      }


      if (
        route ===
        "persona"
      ) {

        renderPersonaPage();

      }


      if (
        route ===
        "history"
      ) {

        renderHistory();

      }


      if (
        route ===
        "profile"
      ) {

        renderProfile();

      }


      navigate(
        route
      );

    }
  );


  document
    .getElementById(
      "signInForm"
    )
    ?.addEventListener(
      "submit",
      signIn
    );


  document
    .getElementById(
      "togglePasswordButton"
    )
    ?.addEventListener(
      "click",
      togglePasswordVisibility
    );


  document
    .getElementById(
      "micButton"
    )
    ?.addEventListener(
      "click",
      toggleRecording
    );


  document
    .getElementById(
      "finishButton"
    )
    ?.addEventListener(
      "click",
      finishConversation
    );


  document
    .getElementById(
      "exitButton"
    )
    ?.addEventListener(
      "click",
      exitConversation
    );


  document
    .getElementById(
      "retryButton"
    )
    ?.addEventListener(
      "click",
      () =>
        startTraining(
          selectedTopic
        )
    );


  document
    .getElementById(
      "newTrainingButton"
    )
    ?.addEventListener(
      "click",
      () =>
        navigate(
          "training"
        )
    );


  document
    .getElementById(
      "feedbackHomeButton"
    )
    ?.addEventListener(
      "click",
      () => {

        renderDashboard();

        navigate(
          "dashboard"
        );

      }
    );


  document
    .getElementById(
      "recommendationButton"
    )
    ?.addEventListener(
      "click",
      startRecommendedTraining
    );


  document
    .getElementById(
      "historyRetryButton"
    )
    ?.addEventListener(
      "click",
      retryHistorySession
    );


  document
    .getElementById(
      "changePasswordButton"
    )
    ?.addEventListener(
      "click",
      toggleChangePasswordPanel
    );


  document
    .getElementById(
      "savePasswordButton"
    )
    ?.addEventListener(
      "click",
      saveNewPassword
    );


  document
    .getElementById(
      "deleteAccountButton"
    )
    ?.addEventListener(
      "click",
      deleteAccount
    );


  document
    .getElementById(
      "signOutButton"
    )
    ?.addEventListener(
      "click",
      signOut
    );


  window.addEventListener(
    "beforeunload",
    cleanupMedia
  );

}


/* =========================================================
   NAVIGATION
   ========================================================= */

function navigate(route) {

  const target =
    pages[route] ||
    pages.dashboard;


  Object
    .values(
      pages
    )
    .forEach(
      page => {

        page
          ?.classList
          .remove(
            "active-page"
          );

      }
    );


  target
    ?.classList
    .add(
      "active-page"
    );


  document
    .querySelectorAll(
      ".nav-item, .mobile-nav-item"
    )
    .forEach(
      item => {

        const trainingChild =
          [
            "persona",
            "conversation",
            "feedback"
          ].includes(
            route
          ) &&
          item.dataset.route ===
          "training";


        const historyChild =
          route ===
          "session-detail" &&
          item.dataset.route ===
          "history";


        const active =
          item.dataset.route ===
          route ||
          trainingChild ||
          historyChild;


        item
          .classList
          .toggle(
            "active",
            active
          );

      }
    );


  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });

}


/* =========================================================
   LOGIN
   ========================================================= */

function signIn(event) {

  event.preventDefault();


  const name =
    document
      .getElementById(
        "nameInput"
      )
      .value
      .trim();


  const email =
    document
      .getElementById(
        "emailInput"
      )
      .value
      .trim();


  const password =
    document
      .getElementById(
        "passwordInput"
      )
      .value;


  if (
    !name ||
    !email ||
    password.length < 6
  ) {

    showToast(
      "أكمل بيانات الدخول."
    );

    return;
  }


  profile = {
    name,
    email,
    passwordSet: true
  };


  localStorage.setItem(
    STORAGE.profile,
    JSON.stringify(
      profile
    )
  );


  updateProfileUI();

  renderDashboard();


  document
    .getElementById(
      "authScreen"
    )
    .classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "appRoot"
    )
    .classList
    .remove(
      "hidden"
    );


  navigate(
    "dashboard"
  );

}


function togglePasswordVisibility() {

  const input =
    document.getElementById(
      "passwordInput"
    );


  const button =
    document.getElementById(
      "togglePasswordButton"
    );


  if (
    !input ||
    !button
  ) {

    return;
  }


  const isHidden =
    input.type ===
    "password";


  input.type =
    isHidden
      ? "text"
      : "password";


  button.textContent =
    isHidden
      ? "إخفاء"
      : "إظهار";

}


/* =========================================================
   PROFILE
   ========================================================= */

function updateProfileUI() {

  if (!profile?.name) {
    return;
  }


  setText(
    "sidebarName",
    profile.name
  );


  setText(
    "profileDisplayName",
    profile.name
  );


  setText(
    "profileEmailText",
    profile.email ||
    "—"
  );


  const firstName =
    profile.name
      .split(/\s+/)[0];


  setText(
    "dashboardGreeting",
    `مرحبًا ${firstName}`
  );

}


function renderProfile() {

  updateProfileUI();


  setText(
    "profileSessionsCount",
    String(
      history.length
    )
  );


  const strongest =
    strongestSkill(
      aggregateSkillScores()
    );


  setText(
    "profileStrongestSkill",
    strongest
      ? strongest.label
      : "—"
  );


  setText(
    "profileLastSession",
    history.length
      ? formatDateShort(
          history[0]
            .createdAt
        )
      : "—"
  );

}


function toggleChangePasswordPanel() {

  document
    .getElementById(
      "changePasswordPanel"
    )
    ?.classList
    .toggle(
      "hidden"
    );

}


function saveNewPassword() {

  const password =
    document
      .getElementById(
        "newPasswordInput"
      )
      ?.value ||
    "";


  const confirmation =
    document
      .getElementById(
        "confirmPasswordInput"
      )
      ?.value ||
    "";


  if (
    password.length < 6
  ) {

    showToast(
      "كلمة المرور يجب أن تكون 6 أحرف على الأقل."
    );

    return;
  }


  if (
    password !==
    confirmation
  ) {

    showToast(
      "كلمتا المرور غير متطابقتين."
    );

    return;
  }


  document
    .getElementById(
      "newPasswordInput"
    )
    .value =
    "";


  document
    .getElementById(
      "confirmPasswordInput"
    )
    .value =
    "";


  document
    .getElementById(
      "changePasswordPanel"
    )
    .classList
    .add(
      "hidden"
    );


  showToast(
    "تم تغيير كلمة المرور."
  );

}


function signOut() {

  cleanupMedia();


  document
    .getElementById(
      "appRoot"
    )
    .classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "authScreen"
    )
    .classList
    .remove(
      "hidden"
    );


  document
    .getElementById(
      "passwordInput"
    )
    .value =
    "";

}


function deleteAccount() {

  if (
    !confirm(
      "هل تريد حذف الحساب وجميع جلسات التدريب؟"
    )
  ) {

    return;
  }


  cleanupMedia();


  profile =
    null;


  history =
    [];


  localStorage.removeItem(
    STORAGE.profile
  );


  localStorage.removeItem(
    STORAGE.history
  );


  document
    .getElementById(
      "appRoot"
    )
    .classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "authScreen"
    )
    .classList
    .remove(
      "hidden"
    );


  document
    .getElementById(
      "nameInput"
    )
    .value =
    "";


  document
    .getElementById(
      "emailInput"
    )
    .value =
    "";


  document
    .getElementById(
      "passwordInput"
    )
    .value =
    "";

}


/* =========================================================
   DASHBOARD
   ========================================================= */

function renderDashboard() {

  updateProfileUI();


  const averages =
    aggregateSkillScores();


  const container =
    document.getElementById(
      "dashboardSkills"
    );


  if (!container) {
    return;
  }


  container.innerHTML =
    "";


  SKILLS.forEach(
    skill => {

      const value =
        averages[
          skill.key
        ];


      const status =
        value == null
          ? {
              label:
                "لم يبدأ",
              className:
                ""
            }
          : qualitativeStatus(
              value
            );


      const card =
        document.createElement(
          "article"
        );


      card.className =
        "dashboard-skill card";


      card.innerHTML = `
        <div class="skill-heading">

          <div class="skill-title">
            <strong>
              ${escapeHtml(skill.label)}
            </strong>
          </div>

          <span class="skill-status ${status.className}">
            ${escapeHtml(status.label)}
          </span>

        </div>

        <div class="skill-track">

          <div
            class="skill-fill"
            style="width:${
              value == null
                ? 0
                : clamp(
                    value,
                    0,
                    100
                  )
            }%"
          ></div>

        </div>
      `;


      container.appendChild(
        card
      );

    }
  );


  setText(
    "sessionsCountLabel",
    history.length
      ? `${history.length} ${
          history.length === 1
            ? "جلسة"
            : "جلسات"
        }`
      : "لا توجد جلسات بعد"
  );


  const strong =
    strongestSkill(
      averages
    );


  const weak =
    weakestSkill(
      averages
    );


  const strength =
    document.getElementById(
      "strengthInsight"
    );


  const focus =
    document.getElementById(
      "focusInsight"
    );


  if (
    !history.length ||
    !strong ||
    !weak
  ) {

    strength.textContent =
      "أكمل أول جلسة ليظهر هنا وصف لنقطة قوتك.";


    focus.textContent =
      "بعد أول تقييم سنحدد المهارة التي تحتاج إلى تركيز أكبر.";

  } else {

    strength.textContent =
      SKILL_STRENGTH_COPY[
        strong.key
      ];


    focus.textContent =
      SKILL_FOCUS_COPY[
        weak.key
      ];

  }


  const recommendation =
    topicRecommendationForSkill(
      weak?.key
    );


  setText(
    "recommendationTitle",
    recommendation.title
  );


  setText(
    "recommendationText",
    recommendation.text
  );

}


function topicRecommendationForSkill(
  skill
) {

  const map = {

    accuracy:
      "kaaba_qiblah",

    evidence:
      "quran_preservation",

    clarity:
      "tawhid",

    listening:
      "prophets",

    wisdom:
      "islam_spread",

    structure:
      "quran_revelation",

    voice:
      "purpose_of_life"

  };


  const id =
    map[skill] ||
    "kaaba_qiblah";


  const item =
    TOPICS.find(
      topicItem =>
        topicItem.id ===
        id
    ) ||
    TOPICS[0];


  return {

    topicId:
      item.id,

    title:
      item.title,

    text:
      item.description

  };

}


function startRecommendedTraining() {

  const weak =
    weakestSkill(
      aggregateSkillScores()
    );


  const recommendation =
    topicRecommendationForSkill(
      weak?.key
    );


  selectedPersona =
    PERSONAS[0];


  selectedTopic =
    TOPICS.find(
      item =>
        item.id ===
        recommendation.topicId
    ) ||
    TOPICS[0];


  startTraining(
    selectedTopic
  );

}


/* =========================================================
   PERSONAS
   ========================================================= */

function personaImage(
  persona
) {

  return `
    <img
      src="${persona.image}"
      alt="${escapeHtml(persona.name)}"
    />
  `;

}


function renderPersonas() {

  const grid =
    document.getElementById(
      "personaGrid"
    );


  if (!grid) {
    return;
  }


  grid.innerHTML =
    "";


  PERSONAS.forEach(
    persona => {

      const card =
        document.createElement(
          "article"
        );


      card.className =
        `persona-card card ${persona.className}`;


      card.tabIndex =
        0;


      card.innerHTML = `
        <div class="persona-avatar">
          ${personaImage(persona)}
        </div>

        <h2>
          ${escapeHtml(persona.name)}
        </h2>

        <p>
          ${escapeHtml(persona.description)}
        </p>

        <div class="persona-meta">

          ${persona.tags
            .map(
              tag =>
                `<span>${escapeHtml(tag)}</span>`
            )
            .join("")}

        </div>

        <span class="persona-open">
          اختيار
        </span>
      `;


      const open =
        () => {

          selectedPersona =
            persona;


          renderPersonaPage();


          navigate(
            "persona"
          );

        };


      card.addEventListener(
        "click",
        open
      );


      card.addEventListener(
        "keydown",
        event => {

          if (
            event.key ===
            "Enter"
          ) {

            open();

          }

        }
      );


      grid.appendChild(
        card
      );

    }
  );

}


function renderPersonaPage() {

  const hero =
    document.getElementById(
      "personaHero"
    );


  if (!hero) {
    return;
  }


  hero.innerHTML = `
    <div class="persona-avatar">
      ${personaImage(selectedPersona)}
    </div>

    <div>

      <span class="mini-label">
        الشخصية المختارة
      </span>

      <h1>
        ${escapeHtml(selectedPersona.name)}
      </h1>

      <p>
        ${escapeHtml(selectedPersona.description)}
      </p>

    </div>
  `;

}


/* =========================================================
   TOPICS
   ========================================================= */

function renderTopicGroups() {

  const root =
    document.getElementById(
      "topicGroups"
    );


  if (!root) {
    return;
  }


  root.innerHTML =
    "";


  TOPIC_GROUPS.forEach(
    group => {

      const section =
        document.createElement(
          "section"
        );


      section.className =
        "topic-group";


      section.innerHTML = `
        <div class="topic-group-head">

          <h3>
            ${escapeHtml(group.title)}
          </h3>

        </div>

        <div class="topic-grid"></div>
      `;


      const grid =
        section.querySelector(
          ".topic-grid"
        );


      group.topics.forEach(
        item => {

          const button =
            document.createElement(
              "button"
            );


          button.type =
            "button";


          button.className =
            "topic-card";


          button.innerHTML = `
            <strong>
              ${escapeHtml(item.title)}
            </strong>

            <span>
              ${escapeHtml(item.description)}
            </span>
          `;


          button.addEventListener(
            "click",
            () =>
              startTraining(
                item
              )
          );


          grid.appendChild(
            button
          );

        }
      );


      root.appendChild(
        section
      );

    }
  );

}


/* =========================================================
   CONVERSATION
   ========================================================= */

async function startTraining(
  topicItem
) {

  cleanupMedia();

  stopTimer();


  selectedTopic =
    topicItem;


  currentSessionId =
    `muhawir_${Date.now()}_${Math.random()
      .toString(36)
      .slice(2, 8)}`;


  currentTranscript = [

    {
      speaker:
        selectedPersona.id,

      text:
        topicItem.opening,

      turn_index:
        0
    }

  ];


  currentEvaluation =
    null;


  sessionStartedAt =
    Date.now();


  try {

    await fetch(
      `/session/reset?session_id=${encodeURIComponent(
        currentSessionId
      )}`,
      {
        method:
          "POST"
      }
    );

  } catch (_) {}


  renderConversation();


  navigate(
    "conversation"
  );


  startTimer();


  setVoiceState(
    "ready"
  );

}


function renderConversation() {

  setText(
    "conversationPersonaName",
    selectedPersona.name
  );


  setText(
    "conversationTopicTitle",
    selectedTopic.title
  );


  const avatar =
    document.getElementById(
      "conversationPersonaIcon"
    );


  if (avatar) {

    avatar.innerHTML =
      personaImage(
        selectedPersona
      );

  }


  const weak =
    weakestSkill(
      aggregateSkillScores()
    );


  const guidance =
    weak
      ? SESSION_GUIDANCE[
          weak.key
        ]
      : [
          "ابدأ بجواب مباشر",
          "تحدث بطبيعتك واشرح الفكرة بوضوح."
        ];


  setText(
    "conversationGuidanceTitle",
    guidance[0]
  );


  setText(
    "conversationGuidanceText",
    guidance[1]
  );


  const thread =
    document.getElementById(
      "conversationThread"
    );


  thread.innerHTML =
    "";


  currentTranscript.forEach(
    turn =>
      appendConversationBubble(
        turn,
        false
      )
  );

}


async function toggleRecording() {

  if (
    requestInProgress
  ) {

    return;

  }


  if (
    recording
  ) {

    stopRecording();

  } else {

    await beginRecording();

  }

}


async function beginRecording() {

  try {

    currentStream =
      await navigator
        .mediaDevices
        .getUserMedia({
          audio:
            true
        });


    const types = [

      "audio/webm;codecs=opus",

      "audio/webm",

      "audio/ogg;codecs=opus",

      "audio/ogg",

      "audio/mp4"

    ];


    mimeType =
      types.find(
        type =>
          MediaRecorder
            .isTypeSupported(
              type
            )
      ) ||
      "";


    mediaRecorder =
      mimeType
        ? new MediaRecorder(
            currentStream,
            {
              mimeType
            }
          )
        : new MediaRecorder(
            currentStream
          );


    if (
      !mimeType
    ) {

      mimeType =
        mediaRecorder
          .mimeType ||
        "audio/webm";

    }


    audioChunks =
      [];


    mediaRecorder.ondataavailable =
      event => {

        if (
          event.data.size
        ) {

          audioChunks.push(
            event.data
          );

        }

      };


    mediaRecorder.onstop =
      sendAudio;


    mediaRecorder.start();


    recording =
      true;


    document
      .getElementById(
        "micButton"
      )
      .classList
      .add(
        "recording"
      );


    setText(
      "micButtonText",
      "اضغط لإيقاف التسجيل"
    );


    document
      .getElementById(
        "finishButton"
      )
      .disabled =
      true;


    document
      .getElementById(
        "exitButton"
      )
      .disabled =
      true;


    setVoiceState(
      "listening"
    );

  } catch (
    error
  ) {

    console.error(
      error
    );


    setVoiceState(
      "error",
      "تعذر الوصول إلى الميكروفون",
      "تأكد من السماح للمتصفح باستخدام الميكروفون."
    );

  }

}


function stopRecording() {

  if (
    !mediaRecorder ||
    mediaRecorder.state ===
      "inactive"
  ) {

    return;

  }


  mediaRecorder.stop();


  recording =
    false;


  document
    .getElementById(
      "micButton"
    )
    .classList
    .remove(
      "recording"
    );


  setText(
    "micButtonText",
    "اضغط للتحدث"
  );


  setRequestBusy(
    true
  );


  setVoiceState(
    "thinking"
  );

}


async function sendAudio() {

  let extension =
    "webm";


  if (
    mimeType.includes(
      "ogg"
    )
  ) {

    extension =
      "ogg";

  }


  if (
    mimeType.includes(
      "mp4"
    )
  ) {

    extension =
      "mp4";

  }


  const audioBlob =
    new Blob(
      audioChunks,
      {
        type:
          mimeType
      }
    );


  stopCurrentStream();


  if (
    !audioBlob.size
  ) {

    setRequestBusy(
      false
    );


    setVoiceState(
      "error",
      "لم يتم تسجيل صوت",
      "حاول مرة أخرى."
    );


    return;

  }


  const formData =
    new FormData();


  formData.append(
    "audio",
    audioBlob,
    `recording.${extension}`
  );


  formData.append(
    "session_id",
    currentSessionId
  );


  formData.append(
    "persona_id",
    selectedPersona.id
  );


  formData.append(
    "topic_id",
    selectedTopic.id
  );


  formData.append(
    "topic_title",
    selectedTopic.title
  );


  formData.append(
    "opening",
    selectedTopic.opening
  );


  try {

    const response =
      await fetch(
        "/talk",
        {
          method:
            "POST",

          body:
            formData
        }
      );


    if (
      !response.ok
    ) {

      throw new Error(
        await readError(
          response
        )
      );

    }


    const data =
      await response.json();


    const trainee =
      {

        speaker:
          "trainee",

        text:
          data.user_text,

        turn_index:
          currentTranscript.length,

        voice_metrics:
          data.voice_metrics ||
          null

      };


    currentTranscript.push(
      trainee
    );


    appendConversationBubble(
      trainee,
      true
    );


    const personaTurn =
      {

        speaker:
          selectedPersona.id,

        text:
          data.adam_text,

        turn_index:
          currentTranscript.length

      };


    currentTranscript.push(
      personaTurn
    );


    appendConversationBubble(
      personaTurn,
      true
    );


    setVoiceState(
      "speaking"
    );


    playPersonaVoice(
      data.adam_audio
    );

  } catch (
    error
  ) {

    console.error(
      error
    );


    setVoiceState(
      "error",
      "تعذر إرسال التسجيل",
      error.message ||
      "حاول مرة أخرى."
    );


    showToast(
      error.message ||
      "تعذر إكمال المحادثة."
    );

  } finally {

    setRequestBusy(
      false
    );

  }

}


function appendConversationBubble(
  turn,
  scroll =
    true
) {

  const thread =
    document.getElementById(
      "conversationThread"
    );


  const trainee =
    turn.speaker ===
    "trainee";


  const wrap =
    document.createElement(
      "div"
    );


  wrap.className =
    `message-wrap ${
      trainee
        ? "trainee"
        : "adam"
    }`;


  const bubble =
    document.createElement(
      "div"
    );


  bubble.className =
    "message-bubble";


  const speaker =
    document.createElement(
      "span"
    );


  speaker.className =
    "message-speaker";


  speaker.textContent =
    trainee
      ? "أنت"
      : selectedPersona.name;


  const text =
    document.createElement(
      "div"
    );


  text.textContent =
    turn.text;


  bubble.append(
    speaker,
    text
  );


  wrap.appendChild(
    bubble
  );


  thread.appendChild(
    wrap
  );


  if (
    scroll
  ) {

    wrap.scrollIntoView({
      behavior:
        "smooth",
      block:
        "end"
    });

  }

}


function playPersonaVoice(
  base64Audio
) {

  if (
    !base64Audio
  ) {

    setVoiceState(
      "ready"
    );

    return;

  }


  if (
    personaAudio
  ) {

    personaAudio.pause();

  }


  personaAudio =
    new Audio(
      `data:audio/mp3;base64,${base64Audio}`
    );


  personaAudio.onended =
    () => {

      personaAudio =
        null;


      setVoiceState(
        "ready",
        "يمكنك الرد الآن",
        "اضغط على الميكروفون عندما تكون جاهزًا."
      );

    };


  personaAudio.onerror =
    () => {

      personaAudio =
        null;


      setVoiceState(
        "ready"
      );

    };


  personaAudio
    .play()
    .catch(
      () =>
        setVoiceState(
          "ready"
        )
    );

}


function setVoiceState(
  state,
  customTitle,
  customText
) {

  const box =
    document.getElementById(
      "voiceState"
    );


  const title =
    document.getElementById(
      "voiceStateTitle"
    );


  const text =
    document.getElementById(
      "voiceStateText"
    );


  box
    ?.classList
    .remove(
      "listening"
    );


  const personaName =
    selectedPersona
      ?.name ||
    "الشخصية";


  const states =
    {

      ready: [
        "جاهز للاستماع",
        "اضغط على الميكروفون وابدأ إجابتك."
      ],

      listening: [
        "أستمع إليك...",
        "اضغط مرة أخرى عند الانتهاء."
      ],

      thinking: [
        `يفكر ${personaName}...`,
        "نجهّز الرد."
      ],

      speaking: [
        `${personaName} يتحدث...`,
        "استمع ثم رد عندما ينتهي."
      ],

      error: [
        "تعذر إكمال الخطوة",
        "حاول مرة أخرى."
      ]

    };


  const defaults =
    states[state] ||
    states.ready;


  title.textContent =
    customTitle ||
    defaults[0];


  text.textContent =
    customText ||
    defaults[1];


  if (
    state ===
    "listening"
  ) {

    box
      ?.classList
      .add(
        "listening"
      );

  }

}


function setRequestBusy(
  value
) {

  requestInProgress =
    value;


  document
    .getElementById(
      "micButton"
    )
    .disabled =
    value;


  document
    .getElementById(
      "finishButton"
    )
    .disabled =
    value ||
    recording;


  document
    .getElementById(
      "exitButton"
    )
    .disabled =
    value ||
    recording;

}


async function exitConversation() {

  if (
    recording
  ) {

    showToast(
      "أوقف التسجيل أولًا."
    );

    return;

  }


  if (
    requestInProgress
  ) {

    return;

  }


  const traineeTurns =
    currentTranscript.filter(
      turn =>
        turn.speaker ===
        "trainee"
    );


  if (
    traineeTurns.length &&
    !confirm(
      "الخروج سيغلق الجلسة دون تقييم أو حفظ. هل تريد المتابعة؟"
    )
  ) {

    return;

  }


  cleanupMedia();

  stopTimer();


  try {

    if (
      currentSessionId
    ) {

      await fetch(
        `/session/reset?session_id=${encodeURIComponent(
          currentSessionId
        )}`,
        {
          method:
            "POST"
        }
      );

    }

  } catch (_) {}


  currentSessionId =
    null;


  currentTranscript =
    [];


  currentEvaluation =
    null;


  renderPersonaPage();


  navigate(
    "persona"
  );

}


async function finishConversation() {

  if (
    recording
  ) {

    showToast(
      "أوقف التسجيل أولًا."
    );

    return;

  }


  if (
    requestInProgress
  ) {

    return;

  }


  const traineeTurns =
    currentTranscript.filter(
      turn =>
        turn.speaker ===
        "trainee"
    );


  if (
    !traineeTurns.length
  ) {

    showToast(
      "ابدأ المحادثة أولًا أو استخدم زر الخروج."
    );

    return;

  }


  if (
    personaAudio
  ) {

    personaAudio.pause();

    personaAudio =
      null;

  }


  stopTimer();


  navigate(
    "feedback"
  );


  showEvaluationLoading();


  try {

    const response =
      await fetch(
        `/evaluate?session_id=${encodeURIComponent(
          currentSessionId
        )}&include_internal=true`,
        {
          method:
            "POST"
        }
      );


    if (
      !response.ok
    ) {

      throw new Error(
        await readError(
          response
        )
      );

    }


    currentEvaluation =
      await response.json();


    renderFeedback(
      currentEvaluation
    );


    saveCurrentSession();

  } catch (
    error
  ) {

    console.error(
      error
    );


    showEvaluationError(
      error.message ||
      "حدث خطأ غير متوقع."
    );

  }

}


/* =========================================================
   FEEDBACK
   ========================================================= */

function showEvaluationLoading() {

  document
    .getElementById(
      "evaluationLoading"
    )
    ?.classList
    .remove(
      "hidden"
    );


  document
    .getElementById(
      "evaluationError"
    )
    ?.classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "evaluationContent"
    )
    ?.classList
    .add(
      "hidden"
    );

}


function showEvaluationError(
  message
) {

  document
    .getElementById(
      "evaluationLoading"
    )
    ?.classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "evaluationContent"
    )
    ?.classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "evaluationError"
    )
    ?.classList
    .remove(
      "hidden"
    );


  setText(
    "evaluationErrorText",
    message
  );

}


function renderFeedback(
  result
) {

  document
    .getElementById(
      "evaluationLoading"
    )
    ?.classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "evaluationError"
    )
    ?.classList
    .add(
      "hidden"
    );


  document
    .getElementById(
      "evaluationContent"
    )
    ?.classList
    .remove(
      "hidden"
    );


  setText(
    "feedbackMeta",
    `${selectedPersona.name} · ${selectedTopic.title}`
  );


  setText(
    "diagnosisHeadline",
    diagnosticHeadline(
      result
    )
  );


  setText(
    "diagnosisText",
    result.coaching
      ?.diagnosis_ar ||
    "تم تحليل الجلسة وتحديد أبرز نقاط القوة والتحسين."
  );


  renderFeedbackSkillBars(
    result
  );


  const errors =
    Array.isArray(
      result.critical_errors
    )
      ? result
          .critical_errors
          .filter(
            Boolean
          )
      : [];


  const critical =
    document.getElementById(
      "criticalErrorCard"
    );


  if (
    errors.length
  ) {

    critical
      ?.classList
      .remove(
        "hidden"
      );


    setText(
      "criticalErrorText",
      errors
        .slice(
          0,
          2
        )
        .join(
          " — "
        )
    );

  } else {

    critical
      ?.classList
      .add(
        "hidden"
      );

  }


  const strengths =
    unique([

      ...(
        result.coaching
          ?.strengths_ar ||
        []
      ),

      ...(
        result.knowledge
          ?.strengths_ar ||
        []
      ),

      ...(
        result.conversation
          ?.strengths_ar ||
        []
      )

    ]).slice(
      0,
      3
    );


  const improvements =
    unique([

      ...(
        result.coaching
          ?.improvements_ar ||
        []
      ),

      ...(
        result.knowledge
          ?.weaknesses_ar ||
        []
      ),

      ...(
        result.conversation
          ?.weaknesses_ar ||
        []
      )

    ]).slice(
      0,
      3
    );


  renderPlainList(
    document.getElementById(
      "strengthsList"
    ),
    strengths,
    "لا توجد ملاحظة إضافية."
  );


  renderPlainList(
    document.getElementById(
      "improvementsList"
    ),
    improvements,
    "لا توجد ملاحظة إضافية."
  );


  renderSources(
    document.getElementById(
      "sourcesList"
    ),
    result.knowledge
      ?.suggested_evidence ||
    []
  );


  setText(
    "nextAttemptText",
    result.coaching
      ?.next_attempt_ar ||
    "طبّق الملاحظة الأهم في المحاولة القادمة."
  );

}


function renderFeedbackSkillBars(
  result
) {

  const container =
    document.getElementById(
      "feedbackSkills"
    );


  if (
    !container
  ) {

    return;

  }


  const scores =
    extractSkillScores(
      result
    );


  container.innerHTML =
    "";


  SKILLS.forEach(
    skill => {

      const value =
        Number.isFinite(
          scores[
            skill.key
          ]
        )
          ? clamp(
              scores[
                skill.key
              ],
              0,
              100
            )
          : 0;


      const row =
        document.createElement(
          "div"
        );


      row.className =
        "feedback-skill-row";


      row.innerHTML = `
        <div class="feedback-skill-label">

          <strong>
            ${escapeHtml(skill.label)}
          </strong>

          <span>
            ${Math.round(value)}%
          </span>

        </div>

        <div class="feedback-skill-track">

          <div
            class="feedback-skill-fill"
            style="width:${value}%"
          ></div>

        </div>
      `;


      container.appendChild(
        row
      );

    }
  );

}


function diagnosticHeadline(
  result
) {

  const knowledge =
    scoreOutOf50(
      result,
      "knowledge"
    );


  const conversation =
    scoreOutOf50(
      result,
      "conversation"
    );


  if (
    knowledge == null ||
    conversation == null
  ) {

    return (
      "ملخص جلستك"
    );

  }


  if (
    knowledge >= 40 &&
    conversation >= 40
  ) {

    return (
      "معرفة قوية وحوار متوازن"
    );

  }


  if (
    knowledge >= 40 &&
    conversation < 32
  ) {

    return (
      "معرفتك قوية وطريقة الإيصال تحتاج إلى تطوير"
    );

  }


  if (
    conversation >= 40 &&
    knowledge < 32
  ) {

    return (
      "أسلوب الحوار جيد والجانب المعرفي يحتاج إلى تثبيت"
    );

  }


  if (
    knowledge < 25
  ) {

    return (
      "راجع المعلومات الأساسية قبل التوسع"
    );

  }


  if (
    conversation < 25
  ) {

    return (
      "تحتاج إلى ممارسة أكبر في طريقة إيصال المعلومة"
    );

  }


  return (
    "أساس جيد مع مساحة واضحة للتحسين"
  );

}


function renderSources(
  container,
  sources
) {

  if (
    !container
  ) {

    return;

  }


  container.innerHTML =
    "";


  const list =
    Array.isArray(
      sources
    )
      ? sources
          .filter(
            Boolean
          )
          .slice(
            0,
            3
          )
      : [];


  if (
    !list.length
  ) {

    container.innerHTML = `
      <div class="empty-state">
        <strong>
          لا توجد مصادر إضافية لهذا الموضوع حاليًا
        </strong>
      </div>
    `;


    return;

  }


  list.forEach(
    source => {

      const card =
        document.createElement(
          "article"
        );


      card.className =
        "source-card";


      const type =
        document.createElement(
          "span"
        );


      type.className =
        "source-type";


      type.textContent =
        sourceTypeLabel(
          source.source_type
        );


      const title =
        document.createElement(
          "h3"
        );


      title.textContent =
        source.citation_label ||
        source.title ||
        source.source_name ||
        "مصدر مرتبط بالموضوع";


      const text =
        document.createElement(
          "p"
        );


      text.textContent =
        source.text ||
        "";


      card.append(
        type,
        title,
        text
      );


      const url =
        safeUrl(
          source.source_url
        );


      if (
        url !==
        "#"
      ) {

        const link =
          document.createElement(
            "a"
          );


        link.href =
          url;


        link.target =
          "_blank";


        link.rel =
          "noopener noreferrer";


        link.textContent =
          "فتح المصدر";


        card.appendChild(
          link
        );

      }


      container.appendChild(
        card
      );

    }
  );

}


/* =========================================================
   HISTORY
   ========================================================= */

function saveCurrentSession() {

  if (
    !currentEvaluation ||
    !currentSessionId
  ) {

    return;

  }


  const traineeTurns =
    currentTranscript.filter(
      turn =>
        turn.speaker ===
        "trainee"
    );


  if (
    !traineeTurns.length
  ) {

    return;

  }


  const record =
    {

      id:
        currentSessionId,

      createdAt:
        new Date()
          .toISOString(),

      durationSeconds:
        sessionStartedAt
          ? Math.round(
              (
                Date.now() -
                sessionStartedAt
              ) /
              1000
            )
          : 0,

      personaId:
        selectedPersona.id,

      topic:
        {
          ...selectedTopic
        },

      transcript:
        currentTranscript.map(
          turn =>
            ({
              ...turn
            })
        ),

      evaluation:
        currentEvaluation

    };


  history =
    [

      record,

      ...history.filter(
        item =>
          item.id !==
          record.id
      )

    ].slice(
      0,
      50
    );


  localStorage.setItem(
    STORAGE.history,
    JSON.stringify(
      history
    )
  );


  renderDashboard();

  renderHistory();

  renderProfile();

}


function renderHistory() {

  const container =
    document.getElementById(
      "historyList"
    );


  if (
    !container
  ) {

    return;

  }


  container.innerHTML =
    "";


  if (
    !history.length
  ) {

    container.innerHTML = `
      <div class="empty-state">

        <strong>
          لا توجد جلسات سابقة
        </strong>

      </div>
    `;


    return;

  }


  history.forEach(
    item => {

      const persona =
        getPersona(
          item.personaId
        );


      const knowledge =
        scoreOutOf50(
          item.evaluation,
          "knowledge"
        );


      const conversation =
        scoreOutOf50(
          item.evaluation,
          "conversation"
        );


      const knowledgeStatus =
        qualitativeStatus(
          knowledge == null
            ? null
            : knowledge * 2
        );


      const conversationStatus =
        qualitativeStatus(
          conversation == null
            ? null
            : conversation * 2
        );


      const card =
        document.createElement(
          "article"
        );


      card.className =
        "history-card card";


      card.tabIndex =
        0;


      card.innerHTML = `
        <div class="history-card-main">

          <div class="persona-avatar">

            ${personaImage(persona)}

          </div>

          <div>

            <span class="mini-label">
              ${escapeHtml(persona.name)}
            </span>

            <h3>
              ${escapeHtml(
                item.topic?.title ||
                "جلسة تدريب"
              )}
            </h3>

            <p>
              ${escapeHtml(
                item.evaluation
                  ?.coaching
                  ?.diagnosis_ar ||
                "جلسة تدريب محفوظة"
              )}
            </p>

          </div>

        </div>


        <div class="history-card-side">

          <time>
            ${escapeHtml(
              formatDate(
                item.createdAt
              )
            )}
          </time>


          <div class="history-card-tags">

            <span class="tiny-level ${knowledgeStatus.className}">

              المعرفة:
              ${escapeHtml(knowledgeStatus.label)}

            </span>


            <span class="tiny-level ${conversationStatus.className}">

              الحوار:
              ${escapeHtml(conversationStatus.label)}

            </span>

          </div>

        </div>
      `;


      const open =
        () => {

          selectedHistoryId =
            item.id;


          renderHistoryDetail();


          navigate(
            "session-detail"
          );

        };


      card.addEventListener(
        "click",
        open
      );


      card.addEventListener(
        "keydown",
        event => {

          if (
            event.key ===
            "Enter"
          ) {

            open();

          }

        }
      );


      container.appendChild(
        card
      );

    }
  );

}


function renderHistoryDetail() {

  const item =
    history.find(
      record =>
        record.id ===
        selectedHistoryId
    );


  if (
    !item
  ) {

    navigate(
      "history"
    );

    return;

  }


  const persona =
    getPersona(
      item.personaId
    );


  const header =
    document.getElementById(
      "historyDetailHeader"
    );


  header.innerHTML = `
    <span class="eyebrow">

      ${escapeHtml(persona.name)}
      ·
      ${escapeHtml(
        formatDate(
          item.createdAt
        )
      )}

    </span>

    <h1>
      ${escapeHtml(
        item.topic?.title ||
        "جلسة تدريب"
      )}
    </h1>
  `;


  const transcript =
    document.getElementById(
      "historyTranscript"
    );


  transcript.innerHTML =
    "";


  (
    item.transcript ||
    []
  ).forEach(
    turn => {

      const block =
        document.createElement(
          "article"
        );


      block.className =
        `transcript-turn ${
          turn.speaker ===
          "trainee"
            ? "trainee"
            : "adam"
        }`;


      const who =
        document.createElement(
          "strong"
        );


      who.textContent =
        turn.speaker ===
        "trainee"
          ? "أنت"
          : persona.name;


      const text =
        document.createElement(
          "p"
        );


      text.textContent =
        turn.text;


      block.append(
        who,
        text
      );


      transcript.appendChild(
        block
      );

    }
  );


  setText(
    "historySummary",
    item.evaluation
      ?.coaching
      ?.diagnosis_ar ||
    "لا يوجد ملخص محفوظ."
  );


  renderHistorySkillSnapshot(
    item.evaluation
  );


  renderPlainList(
    document.getElementById(
      "historyStrengths"
    ),
    unique([

      ...(
        item.evaluation
          ?.coaching
          ?.strengths_ar ||
        []
      ),

      ...(
        item.evaluation
          ?.conversation
          ?.strengths_ar ||
        []
      )

    ]).slice(
      0,
      3
    ),
    "لا توجد ملاحظة إضافية."
  );


  renderPlainList(
    document.getElementById(
      "historyImprovements"
    ),
    unique([

      ...(
        item.evaluation
          ?.coaching
          ?.improvements_ar ||
        []
      ),

      ...(
        item.evaluation
          ?.knowledge
          ?.weaknesses_ar ||
        []
      ),

      ...(
        item.evaluation
          ?.conversation
          ?.weaknesses_ar ||
        []
      )

    ]).slice(
      0,
      3
    ),
    "لا توجد ملاحظة إضافية."
  );

}


function renderHistorySkillSnapshot(
  evaluation
) {

  const container =
    document.getElementById(
      "historySkillSnapshot"
    );


  if (
    !container
  ) {

    return;

  }


  const scores =
    extractSkillScores(
      evaluation
    );


  container.innerHTML =
    "";


  SKILLS.forEach(
    skill => {

      const value =
        Number.isFinite(
          scores[
            skill.key
          ]
        )
          ? clamp(
              scores[
                skill.key
              ],
              0,
              100
            )
          : 0;


      const status =
        qualitativeStatus(
          value
        );


      const row =
        document.createElement(
          "div"
        );


      row.className =
        "snapshot-row";


      row.innerHTML = `
        <span>
          ${escapeHtml(skill.label)}
        </span>

        <div class="snapshot-track">

          <div
            class="snapshot-fill"
            style="width:${value}%"
          ></div>

        </div>

        <span class="snapshot-status">
          ${escapeHtml(status.label)}
        </span>
      `;


      container.appendChild(
        row
      );

    }
  );

}


function retryHistorySession() {

  const item =
    history.find(
      record =>
        record.id ===
        selectedHistoryId
    );


  if (
    !item
  ) {

    return;

  }


  selectedPersona =
    getPersona(
      item.personaId
    );


  selectedTopic =
    item.topic ||
    TOPICS[0];


  startTraining(
    selectedTopic
  );

}


/* =========================================================
   SCORING
   ========================================================= */

function extractSkillScores(
  result
) {

  if (
    !result
  ) {

    return {};

  }


  return {

    accuracy:
      percentOf(
        result.knowledge
          ?.accuracy_score,
        30
      ),

    evidence:
      percentOf(
        result.knowledge
          ?.evidence_score,
        20
      ),

    clarity:
      percentOf(
        result.conversation
          ?.clarity,
        10
      ),

    listening:
      percentOf(
        result.conversation
          ?.listening_response,
        10
      ),

    wisdom:
      percentOf(
        result.conversation
          ?.wisdom_attitude,
        10
      ),

    structure:
      percentOf(
        result.conversation
          ?.answer_structure,
        10
      ),

    voice:
      percentOf(
        result.conversation
          ?.voice_delivery,
        10
      )

  };

}


function aggregateSkillScores() {

  const buckets =
    {};


  SKILLS.forEach(
    skill => {

      buckets[
        skill.key
      ] =
      [];

    }
  );


  history.forEach(
    item => {

      const scores =
        extractSkillScores(
          item.evaluation
        );


      SKILLS.forEach(
        skill => {

          const value =
            scores[
              skill.key
            ];


          if (
            Number.isFinite(
              value
            )
          ) {

            buckets[
              skill.key
            ].push(
              value
            );

          }

        }
      );

    }
  );


  const result =
    {};


  SKILLS.forEach(
    skill => {

      const values =
        buckets[
          skill.key
        ];


      result[
        skill.key
      ] =
        values.length
          ? Math.round(
              values.reduce(
                (
                  sum,
                  value
                ) =>
                  sum +
                  value,
                0
              ) /
              values.length
            )
          : null;

    }
  );


  return result;

}


function strongestSkill(
  values
) {

  return (
    SKILLS
      .map(
        skill =>
          ({
            ...skill,
            value:
              values[
                skill.key
              ]
          })
      )
      .filter(
        item =>
          Number.isFinite(
            item.value
          )
      )
      .sort(
        (
          a,
          b
        ) =>
          b.value -
          a.value
      )[0] ||
    null
  );

}


function weakestSkill(
  values
) {

  return (
    SKILLS
      .map(
        skill =>
          ({
            ...skill,
            value:
              values[
                skill.key
              ]
          })
      )
      .filter(
        item =>
          Number.isFinite(
            item.value
          )
      )
      .sort(
        (
          a,
          b
        ) =>
          a.value -
          b.value
      )[0] ||
    null
  );

}


function scoreOutOf50(
  result,
  side
) {

  if (
    !result
  ) {

    return null;

  }


  const value =
    side ===
    "knowledge"
      ? (
          result.internal_scores
            ?.knowledge ??
          result.knowledge
            ?.total
        )
      : (
          result.internal_scores
            ?.conversation ??
          result.conversation
            ?.total
        );


  const number =
    Number(
      value
    );


  return (
    Number.isFinite(
      number
    )
      ? number
      : null
  );

}


function qualitativeStatus(
  value
) {

  if (
    value == null
  ) {

    return {
      label:
        "غير متاح",
      className:
        ""
    };

  }


  if (
    value >= 80
  ) {

    return {
      label:
        "جيد",
      className:
        "strong"
    };

  }


  if (
    value >= 65
  ) {

    return {
      label:
        "متوسط",
      className:
        "good"
    };

  }


  return {
    label:
      "يحتاج تطوير",
    className:
      "focus"
  };

}


/* =========================================================
   TIMER
   ========================================================= */

function startTimer() {

  stopTimer();


  updateTimer();


  timerHandle =
    setInterval(
      updateTimer,
      1000
    );

}


function updateTimer() {

  if (
    !sessionStartedAt
  ) {

    return;

  }


  const seconds =
    Math.floor(
      (
        Date.now() -
        sessionStartedAt
      ) /
      1000
    );


  const minutes =
    Math.floor(
      seconds /
      60
    );


  setText(
    "sessionTimer",
    `${String(minutes).padStart(2,"0")}:${String(seconds % 60).padStart(2,"0")}`
  );

}


function stopTimer() {

  if (
    timerHandle
  ) {

    clearInterval(
      timerHandle
    );

  }


  timerHandle =
    null;

}


/* =========================================================
   MEDIA
   ========================================================= */

function cleanupMedia() {

  stopCurrentStream();


  if (
    personaAudio
  ) {

    personaAudio.pause();

    personaAudio =
      null;

  }


  if (
    mediaRecorder &&
    mediaRecorder.state !==
      "inactive"
  ) {

    try {

      mediaRecorder.stop();

    } catch (_) {}

  }


  recording =
    false;

}


function stopCurrentStream() {

  if (
    !currentStream
  ) {

    return;

  }


  currentStream
    .getTracks()
    .forEach(
      track =>
        track.stop()
    );


  currentStream =
    null;

}


/* =========================================================
   HELPERS
   ========================================================= */

function getPersona(
  id
) {

  return (
    PERSONAS.find(
      persona =>
        persona.id ===
        id
    ) ||
    PERSONAS[0]
  );

}


function loadJSON(
  key,
  fallback
) {

  try {

    const value =
      localStorage.getItem(
        key
      );


    return value
      ? JSON.parse(
          value
        )
      : fallback;

  } catch (_) {

    return fallback;

  }

}


function setText(
  id,
  value
) {

  const element =
    document.getElementById(
      id
    );


  if (
    element
  ) {

    element.textContent =
      value ??
      "";

  }

}


function percentOf(
  value,
  maximum
) {

  const number =
    Number(
      value
    );


  if (
    value == null ||
    !Number.isFinite(
      number
    )
  ) {

    return null;

  }


  return Math.round(
    (
      number /
      maximum
    ) *
    100
  );

}


function clamp(
  value,
  minimum,
  maximum
) {

  return Math.max(
    minimum,
    Math.min(
      maximum,
      Number(
        value
      )
    )
  );

}


function unique(
  values
) {

  return [
    ...new Set(
      (
        values ||
        []
      ).filter(
        Boolean
      )
    )
  ];

}


function renderPlainList(
  element,
  items,
  emptyText
) {

  if (
    !element
  ) {

    return;

  }


  element.innerHTML =
    "";


  const list =
    (
      items ||
      []
    ).filter(
      Boolean
    );


  if (
    !list.length
  ) {

    const item =
      document.createElement(
        "li"
      );


    item.textContent =
      emptyText;


    element.appendChild(
      item
    );


    return;

  }


  list.forEach(
    value => {

      const item =
        document.createElement(
          "li"
        );


      item.textContent =
        value;


      element.appendChild(
        item
      );

    }
  );

}


function formatDate(
  iso
) {

  try {

    return new Intl
      .DateTimeFormat(
        "ar-SA",
        {
          year:
            "numeric",

          month:
            "short",

          day:
            "numeric",

          hour:
            "2-digit",

          minute:
            "2-digit"
        }
      )
      .format(
        new Date(
          iso
        )
      );

  } catch (_) {

    return "";

  }

}


function formatDateShort(
  iso
) {

  try {

    return new Intl
      .DateTimeFormat(
        "ar-SA",
        {
          month:
            "short",

          day:
            "numeric"
        }
      )
      .format(
        new Date(
          iso
        )
      );

  } catch (_) {

    return "";

  }

}


function sourceTypeLabel(
  type
) {

  const labels =
    {

      quran:
        "القرآن",

      hadith:
        "حديث",

      tafsir:
        "تفسير",

      aqeedah:
        "عقيدة",

      fiqh:
        "فقه",

      sirah:
        "سيرة",

      dawah:
        "دعوة",

      terminology:
        "مصطلحات",

      history:
        "تاريخ",

      qa:
        "سؤال وجواب",

      general:
        "مصدر"

    };


  return (
    labels[type] ||
    "مصدر"
  );

}


function safeUrl(
  value
) {

  try {

    const url =
      new URL(
        value
      );


    return (
      [
        "http:",
        "https:"
      ].includes(
        url.protocol
      )
        ? url.toString()
        : "#"
    );

  } catch (_) {

    return "#";

  }

}


function escapeHtml(
  value
) {

  return String(
    value ??
    ""
  )
    .replaceAll(
      "&",
      "&amp;"
    )
    .replaceAll(
      "<",
      "&lt;"
    )
    .replaceAll(
      ">",
      "&gt;"
    )
    .replaceAll(
      '"',
      "&quot;"
    )
    .replaceAll(
      "'",
      "&#039;"
    );

}


async function readError(
  response
) {

  try {

    const body =
      await response.json();


    return (
      body.detail ||
      body.message ||
      `خطأ من الخادم (${response.status})`
    );

  } catch (_) {

    return (
      `خطأ من الخادم (${response.status})`
    );

  }

}


function showToast(
  message
) {

  const toast =
    document.getElementById(
      "toast"
    );


  if (
    !toast
  ) {

    return;

  }


  toast.textContent =
    message;


  toast
    .classList
    .add(
      "show"
    );


  clearTimeout(
    toastHandle
  );


  toastHandle =
    setTimeout(
      () => {

        toast
          .classList
          .remove(
            "show"
          );

      },
      2500
    );

}

/* Selected measures and source records from the supplied manuscript and bibliography. */
(function (root) {
  const data = {
  "references": {
    "borda": {
      "short": "de Borda (1781)",
      "full": "Jean-Charles de Borda (1781). Mémoire sur les élections au scrutin. Histoire de l’Académie Royale des Sciences, 657–665.",
      "url": "",
      "note": "Historical scoring-rule reference from the supplied bibliography."
    },
    "alcalde": {
      "short": "Alcalde-Unzu & Vorsatz (2013)",
      "full": "Jorge Alcalde-Unzu and Marc Vorsatz (2013). Measuring the cohesiveness of preferences: an axiomatic analysis. Social Choice and Welfare 41(4), 965–988.",
      "url": "https://doi.org/10.1007/s00355-012-0716-9",
      "note": "Cohesiveness measures; paired with the polarization reference below."
    },
    "can": {
      "short": "Can, Özkes & Storcken (2015)",
      "full": "Burak Can, Ali Ihsan Özkes and Ton Storcken (2015). Measuring polarization in preferences. Mathematical Social Sciences 78, 76–79.",
      "url": "https://doi.org/10.1016/j.mathsocsci.2015.09.006",
      "note": "Pairwise polarization; the displayed agreement index is its complement."
    },
    "hashemi": {
      "short": "Hashemi & Endriss (2014)",
      "full": "Vahid Hashemi and Ulle Endriss (2014). Measuring Diversity of Preferences in a Group. Proceedings of ECAI 2014.",
      "url": "https://eprints.illc.uva.nl/id/eprint/504/",
      "note": "Distance-based diversity. Here: expected raw Kendall distance between independent draws."
    },
    "colley": {
      "short": "Colley et al. (2023)",
      "full": "Rachael Colley, Umberto Grandi, César Hidalgo, Mariana Macedo and Carlos Navarrete (2023). Measuring and Controlling Divisiveness in Rank Aggregation. IJCAI 2023, 2616–2623.",
      "url": "https://www.ijcai.org/proceedings/2023/291",
      "note": "§2.2: divisiveness and α-divisiveness; §2.3: per-alternative rank variance."
    },
    "navarrete": {
      "short": "Navarrete et al. (2024)",
      "full": "Carlos Navarrete et al. (2024). Understanding political divisiveness using online participation data from the 2022 French and Brazilian presidential elections. Nature Human Behaviour 8, 137–148.",
      "url": "https://www.nature.com/articles/s41562-023-01755-x",
      "note": "Published online in 2023; 2024 volume/issue, as in the supplied bibliography."
    },
    "delemazure": {
      "short": "Delemazure et al. (2024)",
      "full": "Théo Delemazure, Łukasz Janeczko, Andrzej Kaczmarczyk and Stanisław Szufa (2024). Selecting the Most Conflicting Pair of Candidates. IJCAI 2024, 2766–2773.",
      "url": "https://www.ijcai.org/proceedings/2024/306",
      "note": "§5.1: partitioning ratio and discrepancy; §5.2: balance measures."
    },
    "kendall": {
      "short": "Kendall & Smith (1939)",
      "full": "Maurice G. Kendall and B. Babington Smith (1939). The Problem of m Rankings. Annals of Mathematical Statistics 10(3), 275–287.",
      "url": "https://doi.org/10.1214/aoms/1177732186",
      "note": "Historical rank-agreement background, not an attribution of the new plurality decomposition."
    }
  },
  "measures": [
    {
      "id": "borda",
      "name": "Borda score",
      "scope": "Alternative",
      "level": 2,
      "refs": [
        "borda"
      ],
      "manuscript": "Inventory; Borda and aggregate S-plurality notation.",
      "pages": [
        {
          "title": "Borda is a sum of pairwise wins",
          "body": "\n<p>For a ranking $\\sigma$, let $X_b=\\mathbf1[a\\succ_\\sigma b]$.</p>\n<div class=\"derivation-step\"><h3>1 · Count the alternatives below $a$</h3>\n<div>$$m-r_\\sigma(a)=\\sum_{b\\ne a}X_b.$$</div></div>\n<div class=\"derivation-step\"><h3>2 · Take the average under the profile</h3>\n<div>$$\\mathbb E_\\pi[X_b]=\\Pr_\\pi[a\\succ b]=p_{\\{a,b\\}}^\\pi(a).$$</div></div>\n<div class=\"formal-block derivation-result\"><p>With the deck’s $m,\\ldots,1$ point convention,</p>\n<div>$$B_\\pi(a)=m+1-\\mathbb E_\\pi[r_a]=1+\\sum_{b\\ne a}p_{\\{a,b\\}}^\\pi(a).$$</div>\n<p>Only degree-2 cells are needed.</p></div>\n<p class=\"derivation-convention\">The manuscript uses $R(a):=B_\\pi(a)-1=\\sum_{b\\ne a}p_{ab}$. This shift does not change the winner.</p>"
        }
      ]
    },
    {
      "id": "agreement",
      "name": "Agreement / polarization",
      "scope": "Profile",
      "level": 2,
      "refs": [
        "alcalde",
        "can"
      ],
      "manuscript": "Inventory, pairwise disagreement measures.",
      "pages": [
        {
          "title": "Agreement reads each pair’s imbalance",
          "body": "\n<p>Fix an unordered pair $\\{a,b\\}$ and write $p=p_{\\{a,b\\}}^\\pi(a)$.</p>\n<div class=\"derivation-step\"><h3>1 · Split the population into the two camps</h3>\n<p>The proportions preferring $a$ and $b$ are $p$ and $1-p$.</p>\n<div>$$\\text{imbalance}=|p-(1-p)|=|2p-1|.$$</div></div>\n<div class=\"derivation-step\"><h3>2 · Average across all pairs</h3>\n<div>$$A(\\pi)=\\frac1{\\binom m2}\\sum_{\\{a,b\\}}\\left|2p_{\\{a,b\\}}^\\pi(a)-1\\right|.$$</div></div>\n<div class=\"formal-block derivation-result\"><p>Its polarization complement is</p>\n<div>$$1-A(\\pi)=\\frac1{\\binom m2}\\sum_{\\{a,b\\}}2\\min\\!\\left(p_{ab},1-p_{ab}\\right).$$</div>\n<p>Both measures use degree 2 only; reversing a pair’s orientation changes neither.</p></div>"
        }
      ]
    },
    {
      "id": "kt-diversity",
      "name": "Kendall-distance diversity",
      "scope": "Profile",
      "level": 2,
      "refs": [
        "hashemi"
      ],
      "manuscript": "Inventory, diversity Delta_KT; independent-ranking derivation.",
      "pages": [
        {
          "title": "Kendall diversity counts pairwise reversals",
          "body": "\n<p>Draw two rankings $\\sigma,\\tau$ independently from $\\pi$. Their Kendall distance counts pairs ordered differently.</p>\n<div class=\"derivation-step\"><h3>1 · One pair disagrees in two ways</h3>\n<div>$$\\Pr[a\\succ_\\sigma b,\\ b\\succ_\\tau a]+\\Pr[b\\succ_\\sigma a,\\ a\\succ_\\tau b]$$</div>\n<div>$$=p_{ab}(1-p_{ab})+(1-p_{ab})p_{ab}.$$</div></div>\n<div class=\"derivation-step\"><h3>2 · Sum those indicators and take expectations</h3>\n<div>$$\\Delta_{\\rm KT}(\\pi):=\\mathbb E[d_{\\rm KT}(\\sigma,\\tau)]$$</div></div>\n<div class=\"formal-block derivation-result\">\n<div>$$\\Delta_{\\rm KT}(\\pi)=2\\sum_{\\{a,b\\}}p_{\\{a,b\\}}^\\pi(a)\\left(1-p_{\\{a,b\\}}^\\pi(a)\\right).$$</div>\n<p>Only degree 2 is needed. Independence is between the two sampled rankings, not between pairs within a ranking.</p></div>\n<p class=\"derivation-convention\">We use the expected raw distance. Dividing by $\\binom m2$ changes the scale, not the information required.</p>"
        }
      ]
    },
    {
      "id": "partitioning",
      "name": "Partitioning ratio",
      "scope": "Pair",
      "level": 2,
      "refs": [
        "delemazure"
      ],
      "manuscript": "Inventory, partitioning ratio alpha(a,b).",
      "pages": [
        {
          "title": "Partitioning compares the two camp sizes",
          "body": "\n<p>For $n$ observed voters, let $n_{ab}$ prefer $a$ to $b$ and $n_{ba}=n-n_{ab}$ prefer $b$ to $a$.</p>\n<div class=\"derivation-step\"><h3>1 · Start from the count-based definition</h3>\n<div>$$\\alpha(a,b)=\\frac2n\\min(n_{ab},n_{ba}).$$</div></div>\n<div class=\"derivation-step\"><h3>2 · Replace population shares by their probabilities</h3>\n<div>$$n_{ab}/n\\longrightarrow p_{ab},\\qquad n_{ba}/n\\longrightarrow1-p_{ab}.$$</div></div>\n<div class=\"formal-block derivation-result\">\n<div>$$\\alpha_\\pi(a,b)=2\\min\\!\\left(p_{\\{a,b\\}}^\\pi(a),1-p_{\\{a,b\\}}^\\pi(a)\\right).$$</div>\n<p>One degree-2 cell suffices. The value is 1 for equal camps and 0 for unanimity.</p></div>"
        }
      ]
    },
    {
      "id": "variance",
      "name": "Rank variance",
      "scope": "Alternative",
      "level": 3,
      "refs": [
        "colley",
        "kendall"
      ],
      "manuscript": "Proof of prop:var-splur; inventory Eq. rank-variance.",
      "pages": [
        {
          "title": "Rank variance introduces triple favorites",
          "body": "\n<p>Write $X_b=\\mathbf1[a\\succ b]$ and $R(a)=\\sum_{b\\ne a}p_{ab}=B_\\pi(a)-1$.</p>\n<div class=\"derivation-step\"><h3>1 · Replace rank by the number of wins</h3>\n<div>$$W_a:=\\sum_{b\\ne a}X_b=m-r_a,\\qquad \\operatorname{Var}(r_a)=\\operatorname{Var}(W_a).$$</div></div>\n<div class=\"derivation-step\"><h3>2 · Expand the square</h3>\n<div>$$\\mathbb E[X_b^2]=p_{ab},\\qquad\n\\mathbb E[X_bX_c]=\\Pr[a\\succ b,\\ a\\succ c]=p_{\\{a,b,c\\}}^\\pi(a).$$</div>\n<div>$$\\mathbb E[W_a^2]\n=R(a)+2\\sum_{\\{b,c\\}\\subseteq\\mathcal A\\setminus\\{a\\}}p_{\\{a,b,c\\}}^\\pi(a).$$</div></div>\n<div class=\"formal-block derivation-result\"><p>Subtract the squared mean:</p>\n<div>$$\\operatorname{Var}_\\pi(r_a)\n=R(a)\\bigl(1-R(a)\\bigr)+2\\sum_{\\{b,c\\}\\subseteq\\mathcal A\\setminus\\{a\\}}p_{\\{a,b,c\\}}^\\pi(a).$$</div>\n<p>Pair cells give $R(a)$; triple cells give the joint wins.</p></div>"
        }
      ]
    },
    {
      "id": "navarrete",
      "name": "Navarrete divisiveness",
      "scope": "Alternative",
      "level": 3,
      "refs": [
        "navarrete",
        "colley"
      ],
      "manuscript": "Proof of prop:div-splur; inventory covariance kernel and Eq. navarrete.",
      "pages": [
        {
          "title": "Divisiveness: write the conditional scores",
          "body": "\n<p>For an opponent $b$, compare the Borda scores of $a$ in the two camps. Use $R(a)=B_\\pi(a)-1$; the shift cancels in their difference.</p>\n<div>$$p=p_{ab},\\qquad S_b=\\sum_{c\\ne a,b}p_{ac},\\qquad\nT_b=\\sum_{c\\ne a,b}p_{\\{a,b,c\\}}^\\pi(a).$$</div>\n<div class=\"derivation-step\"><h3>1 · In the camp $a\\succ b$, one win is certain</h3>\n<div>$$R(a\\mid a\\succ b)=1+\\sum_{c\\ne a,b}\n\\frac{\\Pr[a\\succ c,\\ a\\succ b]}p=1+\\frac{T_b}p.$$</div></div>\n<div class=\"derivation-step\"><h3>2 · In the other camp, subtract those joint wins</h3>\n<div>$$\\Pr[a\\succ c,\\ b\\succ a]=p_{ac}-p_{\\{a,b,c\\}}^\\pi(a),$$</div>\n<div>$$R(a\\mid b\\succ a)=\\frac{S_b-T_b}{1-p}.$$</div></div>\n<p class=\"derivation-convention\">These formulas assume $0&lt;p&lt;1$. With an empty camp, set its divisiveness contribution to 0 (Colley et al., Definition 1).</p>"
        },
        {
          "title": "Divisiveness: combine pairs and triples",
          "body": "\n<p>Keep $p=p_{ab}$, $S_b=\\sum_{c\\ne a,b}p_{ac}$ and $T_b=\\sum_{c\\ne a,b}p_{\\{a,b,c\\}}^\\pi(a)$.</p>\n<div class=\"derivation-step\"><h3>3 · Subtract the conditional scores</h3>\n<div>$$1+\\frac{T_b}p-\\frac{S_b-T_b}{1-p}\n=1+\\frac{T_b-pS_b}{p(1-p)}.$$</div></div>\n<div class=\"derivation-step\"><h3>4 · Identify the covariance term</h3>\n<div>$$K_b:=T_b-pS_b\n=\\sum_{c\\ne a,b}\\left(p_{\\{a,b,c\\}}^\\pi(a)-p_{ab}p_{ac}\\right).$$</div></div>\n<div class=\"formal-block derivation-result\"><p>Take absolute differences and average over opponents:</p>\n<div>$$\\operatorname{Div}_\\pi(a)=\\frac1{m-1}\\sum_{b\\ne a}\n\\left|1+\\frac{K_b}{p_{ab}(1-p_{ab})}\\right|.$$</div>\n<p>All inputs have degree at most 3. Empty-camp terms are 0.</p></div>\n<p class=\"derivation-convention\">This is the deck’s raw-Borda scale; normalizing Borda by $m-1$ divides divisiveness by that constant.</p>"
        }
      ]
    },
    {
      "id": "alpha-divisiveness",
      "name": "$\\alpha$-divisiveness · Borda",
      "scope": "Alternative",
      "level": 3,
      "refs": [
        "colley"
      ],
      "manuscript": "Inventory Eq. alpha-div and its conditional-Borda expansion.",
      "pages": [
        {
          "title": "α-divisiveness weights the two camp sizes",
          "body": "\n<p>Let $d_b=|R(a\\mid a\\succ b)-R(a\\mid b\\succ a)|$ and $p=p_{ab}$. We use the appendix’s normalization and $0\\le\\alpha\\le1$.</p>\n<div class=\"derivation-step\"><h3>1 · Start with the weighted conditional difference</h3>\n<div>$$\\operatorname{Div}^{R}_{\\alpha}(a)=\\frac1{m-1}\n\\sum_{b\\ne a}\\bigl(p_{ab}(1-p_{ab})\\bigr)^\\alpha d_b.$$</div></div>\n<div class=\"derivation-step\"><h3>2 · Read conditional probabilities from the matrix</h3>\n<div>$$\\Pr[a\\succ c\\mid a\\succ b]=\\frac{p_{\\{a,b,c\\}}^\\pi(a)}{p_{ab}},$$</div>\n<div>$$\\Pr[a\\succ c\\mid b\\succ a]=\\frac{p_{ac}-p_{\\{a,b,c\\}}^\\pi(a)}{1-p_{ab}}.$$</div></div>\n<p class=\"derivation-convention\">For $c=b$, these probabilities are 1 and 0. Empty camps contribute 0 rather than an undefined conditional expectation.</p>"
        },
        {
          "title": "α-divisiveness needs no new degree",
          "body": "\n<p>Set $S_b=\\sum_{c\\ne a,b}p_{ac}$, $T_b=\\sum_{c\\ne a,b}p_{\\{a,b,c\\}}^\\pi(a)$ and $K_b=T_b-p_{ab}S_b$.</p>\n<div class=\"derivation-step\"><h3>3 · Sum wins within each camp, then subtract</h3>\n<div>$$d_b=\\left|1+\\frac{T_b}{p_{ab}}-\\frac{S_b-T_b}{1-p_{ab}}\\right|\n=\\left|1+\\frac{K_b}{p_{ab}(1-p_{ab})}\\right|.$$</div></div>\n<div class=\"formal-block derivation-result\"><p>Substitute into the weighted average:</p>\n<div>$$\\operatorname{Div}^{R}_{\\alpha}(a)=\\frac1{m-1}\\sum_{b\\ne a}\n[p_{ab}(1-p_{ab})]^\\alpha\n\\left|1+\\frac{K_b}{p_{ab}(1-p_{ab})}\\right|.$$</div>\n<p>The weights use pairs; $K_b$ uses pairs and triples. Degree 3 suffices.</p></div>\n<p class=\"derivation-convention\">Colley et al. allow a factor $c^\\alpha$ (often $c=4$) and normalized Borda. Recover that scale by multiplying by $c^\\alpha/(m-1)$. Neither change affects the level.</p>"
        }
      ]
    },
    {
      "id": "discrepancy",
      "name": "Pairwise discrepancy",
      "scope": "Pair",
      "level": 3,
      "refs": [
        "delemazure"
      ],
      "manuscript": "Inventory Eq. delta and discrepancy beta(a,b).",
      "pages": [
        {
          "title": "Rank distance counts alternatives in between",
          "body": "\n<p>The discrepancy of $a$ and $b$ is $\\beta(a,b)=\\Delta(a,b)/(m-1)$, where $\\Delta(a,b)=\\mathbb E_\\pi[|r_a-r_b|]$.</p>\n<div class=\"derivation-step\"><h3>1 · Express the gap in one ranking</h3>\n<div>$$|r_a-r_b|=1+\\sum_{c\\ne a,b}\\mathbf1[c\\text{ is between }a\\text{ and }b].$$</div></div>\n<div class=\"derivation-step\"><h3>2 · “Between” means above exactly one endpoint</h3>\n<div>$$\\mathbf1[c\\text{ between}]=\\mathbf1[c\\succ a]+\\mathbf1[c\\succ b]\n-2\\mathbf1[c\\succ a,\\ c\\succ b].$$</div></div>\n<div class=\"formal-block derivation-result\"><p>Take expectations:</p>\n<div>$$\\Pr[c\\text{ between }a,b]=2-p_{ac}-p_{bc}-2p_{\\{a,b,c\\}}^\\pi(c).$$</div>\n<p>The last event is exactly a degree-3 plurality cell.</p></div>"
        },
        {
          "title": "Discrepancy is determined by triples",
          "body": "\n<p>Write $R(a)=B_\\pi(a)-1=\\sum_{c\\ne a}p_{ac}$, and likewise for $b$.</p>\n<div class=\"derivation-step\"><h3>3 · Sum over all alternatives in between</h3>\n<div>$$\\Delta(a,b)=1+\\sum_{c\\ne a,b}\n\\left(2-p_{ac}-p_{bc}-2p_{\\{a,b,c\\}}^\\pi(c)\\right).$$</div></div>\n<div class=\"derivation-step\"><h3>4 · Collect the pairwise terms</h3>\n<div>$$\\sum_{c\\ne a,b}(p_{ac}+p_{bc})=R(a)+R(b)-1,$$</div>\n<p>because $p_{ab}+p_{ba}=1$.</p></div>\n<div class=\"formal-block derivation-result\">\n<div>$$\\beta(a,b)=\\frac{2(m-1)-R(a)-R(b)\n-2\\sum_{c\\ne a,b}p_{\\{a,b,c\\}}^\\pi(c)}{m-1}.$$</div>\n<p>Degree 3 suffices; this normalization puts discrepancy in $[0,1]$.</p></div>"
        }
      ]
    }
  ]
};
  if (typeof module !== "undefined" && module.exports) module.exports = data;
  else root.EDDY_LITERATURE = data;
})(typeof window === "undefined" ? globalThis : window);

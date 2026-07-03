const DEFAULT_ROSTER = {
  "enterprise-sales": ["alice", "bob"],
  "eu-sales": ["carla"],
  "sdr-queue": ["dave", "erin", "frank"],
};

const ENTERPRISE_DEAL_SIZE = 50000;

function pickTeam(lead) {
  if (typeof lead.dealSize === "number" && lead.dealSize > ENTERPRISE_DEAL_SIZE) {
    return "enterprise-sales";
  }
  if (lead.region === "EU") {
    return "eu-sales";
  }
  return "sdr-queue";
}

/**
 * Route a batch of leads to a team and an owner (round-robin within team),
 * and produce a notification stub for each assignment.
 * @param {Array<object>} leads
 * @param {{roster?: Record<string,string[]>}} [options]
 */
function routeLeads(leads, options = {}) {
  if (!Array.isArray(leads)) {
    throw new TypeError("leads must be an array");
  }
  const roster = options.roster ?? DEFAULT_ROSTER;
  const cursors = Object.fromEntries(Object.keys(roster).map((team) => [team, 0]));

  const assignments = leads.map((lead) => {
    const team = pickTeam(lead);
    const members = roster[team] ?? [];
    let owner = null;
    if (members.length > 0) {
      owner = members[cursors[team] % members.length];
      cursors[team] += 1;
    }
    return {
      leadId: lead.id,
      assignedTeam: team,
      assignedOwner: owner,
      notification: owner
        ? `stub: would notify ${owner} (via email/slack) about lead ${lead.id ?? "(no id)"}`
        : `stub: no owner available for team ${team}`,
    };
  });

  const byTeam = {};
  for (const a of assignments) {
    byTeam[a.assignedTeam] = (byTeam[a.assignedTeam] ?? 0) + 1;
  }

  return {
    assignments,
    summary: {
      totalLeads: leads.length,
      byTeam,
    },
  };
}

module.exports = { routeLeads, DEFAULT_ROSTER, ENTERPRISE_DEAL_SIZE };

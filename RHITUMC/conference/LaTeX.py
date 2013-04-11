def _timeslot_on_day_has_talks(time_slot_talks, day):
    if time_slot_talks[0] is not None:
        for talk in time_slot_talks[0]:
            if talk.day == day:
                return True
    if time_slot_talks[1] is not None:
        for talk in time_slot_talks[1]:
            if talk.day == day:
                return True
    return False

class LaTeXProgram():
    
    def __init__(self, opts, sessions, special_sessions, time_slots, tracks, days):
        
        self.opts = opts
        self.sessions = sessions
        self.special_sessions = special_sessions
        self.time_slots = time_slots
        self.tracks = tracks
        self.days = days
        self.doc = '''\\documentclass{article}

\\begin{document}

\\section*{Program At-A-Glance}

%s

\\newpage

\\section*{Program - Plenary Speakers}

%s

\\newpage

\\section*{Program - Undergraduate Talks}

%s

\\end{document}
'''

    def generate_program(self):
        return self.doc % (self.build_table_of_contents(), self.build_special_sessions(), self.build_student_talks())

    def build_table_of_contents(self):
        return self.build_header() + self.build_body()
        
    def build_body(self):
        time_session_dict = {}
        for slot in self.time_slots:
            time_session_dict[slot] = [None, None] #[regular sessions, special sessions]
        for session in self.sessions:
            if time_session_dict[session.time][0] is None:
                time_session_dict[session.time][0] = []
            time_session_dict[session.time][0].append(session)
        for special_session in self.special_sessions:
            if time_session_dict[special_session.time][1] is None:
                time_session_dict[special_session.time][1] = special_session
        body = ''
        for day in self.days:
            for time_slot in self.time_slots:
                if _timeslot_on_day_has_talks(time_session_dict[time_slot], day):
                    body += '%s %s \\\\\n%s\n' % (time_slot, '& ' * len(self.tracks), day)
                    if time_session_dict[time_slot][1] is not None:
                        body += '& \\multicolumn{%s}{c|}{%s, %s} \\\\ \n' % \
                         (len(self.tracks), time_session_dict[time_slot][1].room, time_session_dict[time_slot][1].short_description)
                        if time_session_dict[time_slot][1].short_title != '':
                            body += '& \\multicolumn{%s}{c|}{%s, %s} \\\\\n' % (len(self.tracks), time_session_dict[time_slot][1].speaker,\
                                                                                 time_session_dict[time_slot][1].short_title)
                        else:
                            body += '& \\multicolumn{%s}{c|}{%s} \\\\\n' % (len(self.tracks), time_session_dict[time_slot][1].speaker)
                    elif time_session_dict[time_slot][0] is not None:
                        temp1 = ''
                        temp2 = ''
                        temp3 = ''
                        for track in self.tracks:
                            #Sessions will be sorted correctly based on Tracks from the view
                            has_talk = False
                            for session in time_session_dict[time_slot][0]:
                                if session.track == track and session.day == day:
                                    temp1 += '& \\parbox{4cm}{\\centering %s}' % ';\n'.join([str(s) for s in session.speakers.all()])
                                    temp2 += '& \\parbox{4cm}{\\centering %s} ' % session.speakers.all()[0].school
                                    temp3 += '& \\parbox{4cm}{\\centering %s} ' % session.speakers.all()[0].paper_title
                                    has_talk = True
                                    break
                            if not has_talk:
                                temp1 += '& '
                                temp2 += '& '
                                temp3 += '& '
                        temp1 += ' \\\\\n'
                        temp2 += ' \\\\\n'
                        temp3 += ' \\\\\n'
                        
                        body += temp1
                        if self.opts['display_schools']:
                            body += temp2
                        if self.opts['display_titles']:
                            body += temp3
                    else:
                        temp = '& ' * len(self.tracks)
                        body += ('%s\\\\\n' % temp) * 2
                    body += '\\hline\n'
            body += '\\hline\n'
        body += '\\end{tabular}'
        return body
        
    def build_header(self):
        header1 = '\\begin{tabular}{c||%s}\n' % ('c|' * len(self.tracks))
        header2 = ''
        for track in self.tracks:
            header1 += '& \\multicolumn{1}{c|}{\\bf %s}\n' % track.name
            header2 += '& \\multicolumn{1}{c|}{\\bf Room %s}\n' % track.room.room_number
        header1 += ' \\\\\n'
        header2 += ' \\\\\n\\hline\n'
        return header1 + header2
        
    def build_special_sessions(self):
        body = ''
        for session in self.special_sessions:
            if session.has_page_in_program:
                body += self.build_single_session(session)
        return body

    def build_single_session(self, session):
        return '\\noindent{\\bf %s \\\\\n%s \\\\\nRoom: %s \\\\\nTime: %s \\\\\nDate: %s}\n\n\\bigskip\n\n\\noindent{\\bf About %s}\n\n\\medskip\n\n%s\n\n' % (session.speaker, session.long_title, session.room, session.time, session.day, session.speaker, session.long_description)

    def build_student_talks(self):
        body = ''
        for session in self.sessions:
            body += self.build_single_talk(session)
        return body
    
    def build_single_talk(self, talk):
        speakers = talk.speakers.all()
        body = '\\noindent{\\bf '
        for speaker in speakers:
            body += '%s-%s, ' % (str(speaker), speaker.school)
        body = body[:-2]
        body += ' \\\\\n'
        body += '%s \\\\\n' % speakers[0].paper_title
        body += '%s %s in %s}\n\n' % (talk.day, talk.time, talk.track.room)
        body += '\\medskip\n\n%s\n\n\\bigskip\n\n' % speakers[0].paper_abstract
        return body
        
class LaTeXBadges():
    
    def __init__(self, opts, attendees):
        
        self.opts = opts
        self.attendees = attendees
        
        self.doc = '''%%Based on http://psy.swan.ac.uk/staff/carter/unix/latex_badges.htm
\\documentclass[12pt]{article}
\\usepackage{fullpage}
\\usepackage{filecontents}
\\usepackage{csvtools}
\\usepackage{fix-cm}

\\pagestyle{empty}

\\setlength{\\oddsidemargin}{-12mm}

\\begin{filecontents*}{names.csv}
Name, Affiliation
%s
\\end{filecontents*}
\\begin{document}

\\applyCSVfile{names.csv}{%%
    \\noindent
        \\fbox{\\begin{minipage}[t][%smm]{%smm}
            \\vspace{15mm}

            \\sffamily \\centering
                \\fontsize{30}{36}\\selectfont\\insertName
                \\LARGE \\vspace{10mm}

                \\itshape\\insertAffiliation

            \\end{minipage}}
        \\hspace{2mm}
        \\vspace{2mm}
}

\\end{document}
'''
    def generate_badges(self):
        return self.doc % (self.aggregate_names(), self.opts['width'], self.opts['height'])
    
    def aggregate_names(self):
        names = ''
        for attendee in self.attendees:
            names += '%s %s, %s\n' % (attendee.first_name, attendee.last_name, attendee.school)
        return names
    
    def get_badge_dimensions(self):
        return 
        
        
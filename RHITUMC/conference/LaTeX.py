class LaTeXFile():
    
    def __init__(self, sessions, special_sessions, time_slots, tracks):
        
        self.sessions = sessions
        self.special_sessions = special_sessions
        self.time_slots = time_slots
        self.tracks = tracks
        self.doc = '''
                    \documentclass{article}

                    \begin{document}

                    \section*{Program At-A-Glance}
                    
                    %s
                    
                    \newpage

                    \section*{Program - Plenary Speakers}
                    
                    %s
                    
                    \newpage

                    \section*{Program - Undergraduate Talks}
                    
                    %s
                    
                    \end{document}
                    '''

    def build_table_of_contents(self):
        '''
            \begin{tabular}{c||c|c|c|c|}
            & \multicolumn{1}{c|}{\bf Track A} & 
                \multicolumn{1}{c|}{\bf Track B} & 
                \multicolumn{1}{c|}{\bf Track C} & 
                \multicolumn{1}{c|}{\bf Track D} \\
            & \multicolumn{1}{c|}{\bf Room G219} & 
                \multicolumn{1}{c|}{\bf Room G220} & 
                \multicolumn{1}{c|}{\bf Room G221} & 
                \multicolumn{1}{c|}{\bf Room G222} \\
            \hline
            1:35 - 1:40 
                & \multicolumn{4}{c|}{Room E104, Introductory Comments from} \\
                & \multicolumn{4}{c|}{President Robert Coons}\\
            \hline
            1:40 - 2:25 
                & \multicolumn{4}{c|}{Room E104, Plenary Talk} \\
                & \multicolumn{4}{c|}{Dr. Thomas Mifflin, Metron} \\
            \hline
            2:30 - 3:50 & Speaker 1 & Speaker 2 & Speaker 3 & Speaker 4 \\
                & School 1 & School 2 & School 3 & School 4 \\
            \hline
            3:55 - 4:15 & Speaker 1 & Speaker 2 & Speaker 3 & Speaker 4 \\
                & School 1 & School 2 & School 3 & School 4 \\
            \hline
            4:20 - 4:40 & Speaker 1 & Speaker 2 & Speaker 3 & Speaker 4 \\
                & School 1 & School 2 & School 3 & School 4 \\
            \hline
            4:45 - 5:05 & Speaker 1 & Speaker 2 & Speaker 3 & Speaker 4 \\
                & School 1 & School 2 & School 3 & School 4 \\
            \hline
            5:30 - 6:45
                & \multicolumn{4}{c|}{Faculty Dinning Area, Hulman Union} \\
                & \multicolumn{4}{c|}{Dinner} \\
            \hline
            7:00 - 8:00
                & \multicolumn{4}{c|}{Room E104, Plenary talk} \\
                & \multicolumn{4}{c|}{Dr. Tony Nance, Mathematical Biosciences Institute} \\
            \hline \hline
            8:30 - 8:50 & Speaker 1 & Speaker 2 & Speaker 3 & Speaker 4 \\
                & School 1 & School 2 & School 3 & School 4 \\
            \hline
            \end{tabular}
            '''
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
        for time_slot in self.time_slots:
            body += '%s - %s\n' % (time_slot.start_time, time_slot.end_time)
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
                for track in self.tracks:
                    #Sessions will be sorted correctly based on Tracks from the view
                    has_talk = False
                    for session in time_session_dict[time_slot][0]:
                        if session.track == track:
                            temp1 += '& %s ' % ', '.join([str(s) for s in session.speakers.all()])
                            temp2 += '& %s ' % session.speakers.all()[0].school
                            has_talk = True
                            break
                    if not has_talk:
                        temp1 += '& '
                        temp2 += '& '
                temp1 += ' \\\\\n'
                temp2 += ' \\\\\n'
                body += temp1 + temp2
            else:
                temp = '& ' * len(self.tracks)
                body += ('%s\\\\\n' % temp) * 2
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
        body = '\section*{Program - Plenary Speakers}\n\n'
        for session in self.special_sessions:
            if session.has_page_in_program:
                body += self.build_single_session(session)
        return body
        

    def build_single_session(self, session):
        return '\\noindent{\\bf %s \\\\\n%s \\\\\nRoom: %s \\\\\nTime: %s \\\\\nDate: %s}\n\n\\bigskip\n\n\\noindent{\\bf About %s}\n\n\\medskip\n\n%s\n\n\\newpage' % (session.speaker, session.long_title, session.room, session.time, session.day, session.speaker, session.long_description)

    def build_student_talks(self):
        pass
